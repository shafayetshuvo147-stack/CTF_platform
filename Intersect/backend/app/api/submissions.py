from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from collections import defaultdict

from app.core.db import get_db
from app.core.config import settings
from app.models.models import Submission, Instance, User, Challenge
from app.schemas import SubmissionCreate, SubmissionOut, SubmissionHistoryOut
from app.api.auth import get_current_user
from app.services.scoring import effective_points

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/", response_model=SubmissionOut)
def submit_flag(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    flag = payload.flag.strip()
    if not flag:
        raise HTTPException(status_code=400, detail="Flag cannot be empty")

    challenge = db.query(Challenge).filter(Challenge.id == payload.challenge_id, Challenge.is_active == True).first()  # noqa: E712
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

    # Rate limiting: check recent submissions in the last minute
    one_min_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
    recent_submissions_count = (
        db.query(Submission)
        .filter(Submission.user_id == user.id, Submission.submitted_at >= one_min_ago)
        .count()
    )
    if recent_submissions_count >= settings.RATE_LIMIT_SUBMISSIONS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many flag submissions. Please slow down and try again in a minute."
        )

    # Check if already solved by this user
    already_solved = (
        db.query(Submission)
        .filter(
            Submission.user_id == user.id,
            Submission.challenge_id == payload.challenge_id,
            Submission.correct == True,  # noqa: E712
        )
        .first()
    )
    if already_solved:
        return SubmissionOut(correct=False, message="Challenge already solved!", points_awarded=0)

    # Check against the user's active/created instances for this challenge
    matching_instance = (
        db.query(Instance)
        .filter(
            Instance.user_id == user.id,
            Instance.challenge_id == payload.challenge_id,
            Instance.flag_value == flag,
        )
        .first()
    )

    correct = matching_instance is not None

    submission = Submission(
        user_id=user.id,
        challenge_id=payload.challenge_id,
        submitted_flag=flag,
        correct=correct,
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    db.commit()

    if correct:
        # Calculate points for this solve
        all_correct_subs = db.query(Submission).filter(
            Submission.challenge_id == payload.challenge_id,
            Submission.correct == True,  # noqa: E712
        ).all()
        solve_users = {s.user_id for s in all_correct_subs}
        pts = effective_points(challenge.points, len(solve_users))
        return SubmissionOut(
            correct=True,
            message="Congratulations! Correct flag submitted!",
            points_awarded=pts,
        )

    return SubmissionOut(
        correct=False,
        message="Incorrect flag. Please verify and try again.",
        points_awarded=0,
    )


@router.get("/mine", response_model=List[SubmissionHistoryOut])
def my_submissions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    submissions = (
        db.query(Submission)
        .filter(Submission.user_id == user.id)
        .order_by(Submission.submitted_at.desc())
        .limit(100)
        .all()
    )

    challenges = {c.id: c for c in db.query(Challenge).all()}

    results = []
    for s in submissions:
        c = challenges.get(s.challenge_id)
        results.append(
            SubmissionHistoryOut(
                id=s.id,
                challenge_id=s.challenge_id,
                challenge_name=c.name if c else "Unknown Challenge",
                challenge_category=c.category if c else "unknown",
                submitted_flag=s.submitted_flag,
                correct=s.correct,
                submitted_at=s.submitted_at,
            )
        )
    return results

