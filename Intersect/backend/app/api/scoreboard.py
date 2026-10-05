from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from collections import defaultdict
from datetime import datetime, timezone

from app.core.db import get_db
from app.models.models import Submission, Challenge, User
from app.schemas import ScoreboardEntry
from app.services.scoring import effective_points

router = APIRouter(prefix="/scoreboard", tags=["scoreboard"])


@router.get("/", response_model=List[ScoreboardEntry])
def get_scoreboard(db: Session = Depends(get_db)):
    correct_submissions = (
        db.query(Submission)
        .filter(Submission.correct == True)  # noqa: E712
        .order_by(Submission.submitted_at.asc())
        .all()
    )

    # 1. Count distinct users per challenge (for dynamic decay points)
    solve_users = defaultdict(set)
    user_solved_challenges = defaultdict(set)
    user_last_solve_time = {}

    for s in correct_submissions:
        solve_users[s.challenge_id].add(s.user_id)
        user_solved_challenges[s.user_id].add(s.challenge_id)
        # Update last solve time
        if s.user_id not in user_last_solve_time or s.submitted_at > user_last_solve_time[s.user_id]:
            user_last_solve_time[s.user_id] = s.submitted_at

    challenges = {c.id: c for c in db.query(Challenge).all()}
    users = {u.id: u for u in db.query(User).all()}

    # 2. Compute dynamic scores per user
    user_data = []
    epoch_min = datetime(1970, 1, 1, tzinfo=timezone.utc)

    for user_id, user in users.items():
        solved_ids = user_solved_challenges.get(user_id, set())
        total_score = 0
        for cid in solved_ids:
            chal = challenges.get(cid)
            if chal:
                total_score += effective_points(chal.points, len(solve_users[cid]))

        last_time = user_last_solve_time.get(user_id, epoch_min)
        user_data.append({
            "username": user.username,
            "score": total_score,
            "solves": len(solved_ids),
            "last_solve_time": last_time,
        })

    # 3. Sort: Highest score first, then earliest last solve time (tie-breaker)
    user_data.sort(
        key=lambda x: (-x["score"], x["last_solve_time"])
    )

    # 4. Form scoreboard entries with rank
    board = []
    for idx, item in enumerate(user_data):
        board.append(
            ScoreboardEntry(
                rank=idx + 1,
                username=item["username"],
                score=item["score"],
                solves=item["solves"],
            )
        )

    return board

