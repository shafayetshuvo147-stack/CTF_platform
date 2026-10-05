import os
import yaml
import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import SessionLocal, Base, engine
from app.models.models import Challenge

logger = logging.getLogger(__name__)


def seed_challenges(challenges_dir: str = None) -> tuple[int, int]:
    """
    Scans the challenges directory for challenge.yaml files and upserts them
    into the database.
    """
    if not challenges_dir:
        challenges_dir = settings.CHALLENGES_DIR

    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    count_added = 0
    count_updated = 0

    if not os.path.isdir(challenges_dir):
        logger.warning("Challenges directory not found: %s", challenges_dir)
        db.close()
        return 0, 0

    try:
        for entry in sorted(os.listdir(challenges_dir)):
            chal_path = os.path.join(challenges_dir, entry)
            if not os.path.isdir(chal_path):
                continue

            yaml_path = os.path.join(chal_path, "challenge.yaml")
            if not os.path.isfile(yaml_path):
                continue

            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    meta = yaml.safe_load(f)
            except Exception as e:
                logger.error("Failed to read %s: %s", yaml_path, e)
                continue

            if not meta or "slug" not in meta:
                continue

            existing = db.query(Challenge).filter(Challenge.slug == meta["slug"]).first()
            if existing:
                for key in ("name", "category", "description", "points", "docker_image", "container_port", "flag_env_var"):
                    if key in meta:
                        setattr(existing, key, meta[key])
                existing.is_active = meta.get("is_active", True)
                count_updated += 1
            else:
                db.add(Challenge(
                    slug=meta["slug"],
                    name=meta.get("name", meta["slug"]),
                    category=meta.get("category", "misc"),
                    description=meta.get("description", "").strip(),
                    points=meta.get("points", 100),
                    docker_image=meta.get("docker_image", f"intersect/{meta['slug']}:latest"),
                    container_port=meta.get("container_port", 5000),
                    flag_env_var=meta.get("flag_env_var", "FLAG"),
                    is_active=meta.get("is_active", True),
                ))
                count_added += 1

        db.commit()
    finally:
        db.close()

    return count_added, count_updated
