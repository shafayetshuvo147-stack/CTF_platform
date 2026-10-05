from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from collections import defaultdict

from app.core.db import get_db
from app.models.models import Challenge, Submission
from app.schemas import ChallengeOut
from app.services.scoring import effective_points

router = APIRouter(prefix="/challenges", tags=["challenges"])


def get_challenge_difficulty(points: int) -> str:
    if points <= 125:
        return "Easy"
    elif points <= 220:
        return "Medium"
    elif points <= 300:
        return "Hard"
    return "Insane"


@router.get("/", response_model=List[ChallengeOut])
def list_challenges(db: Session = Depends(get_db)):
    challenges = db.query(Challenge).filter(Challenge.is_active == True).all()  # noqa: E712
    correct_subs = db.query(Submission).filter(Submission.correct == True).all()  # noqa: E712

    solve_users = defaultdict(set)
    for s in correct_subs:
        solve_users[s.challenge_id].add(s.user_id)

    results = []
    for c in challenges:
        solves = len(solve_users.get(c.id, set()))
        dyn_points = effective_points(c.points, solves)
        diff = get_challenge_difficulty(c.points)
        results.append(
            ChallengeOut(
                id=c.id,
                slug=c.slug,
                name=c.name,
                category=c.category,
                description=c.description or "",
                points=dyn_points,
                difficulty=diff,
                details=f"Target parameter analysis for {c.name}",
                solves_count=solves,
                is_solved=False,
            )
        )
    return results


@router.get("/{challenge_id}", response_model=ChallengeOut)
def get_challenge(challenge_id: str, db: Session = Depends(get_db)):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.is_active == True).first()  # noqa: E712
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

    correct_subs = db.query(Submission).filter(
        Submission.challenge_id == challenge_id,
        Submission.correct == True  # noqa: E712
    ).all()
    solve_users = {s.user_id for s in correct_subs}
    solves = len(solve_users)
    dyn_points = effective_points(challenge.points, solves)

    return ChallengeOut(
        id=challenge.id,
        slug=challenge.slug,
        name=challenge.name,
        category=challenge.category,
        description=challenge.description or "",
        points=dyn_points,
        difficulty=get_challenge_difficulty(challenge.points),
        details=f"Target parameter analysis for {challenge.name}",
        solves_count=solves,
        is_solved=False,
    )

