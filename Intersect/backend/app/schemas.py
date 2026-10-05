from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: EmailStr
    is_admin: bool


class UserProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: EmailStr
    is_admin: bool
    created_at: Optional[datetime] = None
    score: int = 0
    rank: Optional[int] = None
    solves_count: int = 0
    solved_challenge_ids: List[str] = []


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChallengeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    name: str
    category: str
    description: str
    points: int
    difficulty: Optional[str] = "Easy"
    details: Optional[str] = ""
    solves_count: Optional[int] = 0
    is_solved: Optional[bool] = False


class InstanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    challenge_id: str
    host_port: int
    status: str
    started_at: datetime
    expires_at: datetime
    connect_info: str


class SubmissionCreate(BaseModel):
    challenge_id: str
    flag: str = Field(..., min_length=1, max_length=256)


class SubmissionOut(BaseModel):
    correct: bool
    message: str
    points_awarded: Optional[int] = 0


class SubmissionHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    challenge_id: str
    challenge_name: Optional[str] = None
    challenge_category: Optional[str] = None
    submitted_flag: str
    correct: bool
    submitted_at: datetime


class ScoreboardEntry(BaseModel):
    rank: Optional[int] = None
    username: str
    score: int
    solves: int

