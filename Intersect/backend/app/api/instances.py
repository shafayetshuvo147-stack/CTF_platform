from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.core.config import settings
from app.models.models import Instance, Challenge, User
from app.schemas import InstanceOut
from app.services import orchestrator, flag_generator
from app.api.auth import get_current_user

router = APIRouter(prefix="/instances", tags=["instances"])


def _to_utc(dt: datetime) -> datetime:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _to_out(instance: Instance) -> InstanceOut:
    host = settings.CHALLENGE_HOST
    return InstanceOut(
        id=instance.id,
        challenge_id=instance.challenge_id,
        host_port=instance.host_port,
        status=instance.status,
        started_at=instance.started_at,
        expires_at=instance.expires_at,
        connect_info=f"{host}:{instance.host_port}",
    )


@router.post("/{challenge_id}/start", response_model=InstanceOut)
def start_instance(
    challenge_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Run lazy expiry cleanup first
    orchestrator.cleanup_expired_instances(db)

    challenge = db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.is_active == True).first()  # noqa: E712
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

    now_utc = datetime.now(timezone.utc)

    # Check for existing running instance for this user & challenge
    existing = (
        db.query(Instance)
        .filter(
            Instance.user_id == user.id,
            Instance.challenge_id == challenge_id,
            Instance.status == "running",
        )
        .first()
    )

    if existing:
        # Check if already expired or container crashed
        exp_utc = _to_utc(existing.expires_at)
        if exp_utc <= now_utc or not orchestrator.is_running(existing.container_id):
            orchestrator.stop_instance(existing.container_id)
            existing.status = "expired"
            db.commit()
        else:
            return _to_out(existing)

    # Check user concurrency limit
    active_count = (
        db.query(Instance)
        .filter(Instance.user_id == user.id, Instance.status == "running")
        .count()
    )
    if active_count >= settings.MAX_INSTANCES_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You have reached the maximum active instances limit ({settings.MAX_INSTANCES_PER_USER}). Please stop an active instance before starting a new one."
        )

    # Collect currently allocated ports across active instances to avoid collisions
    running_instances = db.query(Instance).filter(Instance.status == "running").all()
    used_ports = {inst.host_port for inst in running_instances}

    flag_value = flag_generator.generate_flag(challenge.slug, user.id)
    result = orchestrator.start_instance(
        slug=challenge.slug,
        docker_image=challenge.docker_image,
        container_port=challenge.container_port,
        flag_env_var=challenge.flag_env_var,
        flag_value=flag_value,
        user_id=user.id,
        active_ports=used_ports,
    )

    instance = Instance(
        user_id=user.id,
        challenge_id=challenge_id,
        container_id=result["container_id"],
        host_port=result["host_port"],
        flag_value=flag_value,
        status="running",
        started_at=now_utc,
        expires_at=now_utc + timedelta(seconds=settings.INSTANCE_TTL_SECONDS),
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return _to_out(instance)


@router.post("/{instance_id}/stop")
def stop_instance(
    instance_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    instance = (
        db.query(Instance)
        .filter(Instance.id == instance_id, Instance.user_id == user.id)
        .first()
    )
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")

    if instance.status == "running":
        orchestrator.stop_instance(instance.container_id)
        instance.status = "stopped"
        db.commit()

    return {"status": "stopped"}


@router.get("/mine", response_model=List[InstanceOut])
def my_instances(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Run lazy expiry cleanup first
    orchestrator.cleanup_expired_instances(db)

    instances = (
        db.query(Instance)
        .filter(Instance.user_id == user.id, Instance.status == "running")
        .order_by(Instance.started_at.desc())
        .all()
    )
    return [_to_out(i) for i in instances]

