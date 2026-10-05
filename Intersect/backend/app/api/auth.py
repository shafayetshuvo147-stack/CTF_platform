from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from collections import defaultdict

from app.core.db import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.models.models import User, Submission, Challenge
from app.schemas import UserCreate, UserOut, UserProfileOut, Token
from app.services.scoring import effective_points

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    username = payload.username.strip()
    email = payload.email.strip().lower()

    if not username or len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")

    if db.query(User).filter(User.username.ilike(username)).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email.ilike(email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = form_data.username.strip()
    user = db.query(User).filter(User.username.ilike(username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(subject=user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserProfileOut)
def get_current_user_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Calculate current score and solved challenges
    correct_subs = db.query(Submission).filter(Submission.correct == True).all()  # noqa: E712
    challenges = {c.id: c for c in db.query(Challenge).all()}

    # Distinct user solves per challenge
    solve_users = defaultdict(set)
    user_solves = defaultdict(set)
    for s in correct_subs:
        solve_users[s.challenge_id].add(s.user_id)
        user_solves[s.user_id].add(s.challenge_id)

    # Compute all user scores for ranking
    user_scores = defaultdict(int)
    for uid, chals in user_solves.items():
        for cid in chals:
            chal = challenges.get(cid)
            if chal:
                user_scores[uid] += effective_points(chal.points, len(solve_users[cid]))

    sorted_ranks = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    rank = None
    for idx, (uid, _) in enumerate(sorted_ranks):
        if uid == user.id:
            rank = idx + 1
            break

    my_solved_chals = list(user_solves.get(user.id, set()))
    my_score = user_scores.get(user.id, 0)

    return UserProfileOut(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        created_at=user.created_at,
        score=my_score,
        rank=rank,
        solves_count=len(my_solved_chals),
        solved_challenge_ids=my_solved_chals,
    )

