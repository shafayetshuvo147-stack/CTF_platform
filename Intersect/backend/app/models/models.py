import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from app.core.db import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)

    team = relationship("Team", back_populates="members")
    instances = relationship("Instance", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=now)

    members = relationship("User", back_populates="team")


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(String, primary_key=True, default=gen_uuid)
    slug = Column(String, unique=True, index=True, nullable=False)   # matches challenges/<slug>/ dir
    name = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)            # web, pwn, crypto, forensics, etc.
    description = Column(Text, default="")
    points = Column(Integer, default=100)
    docker_image = Column(String, nullable=False)         # built image tag
    container_port = Column(Integer, nullable=False)      # port the challenge service listens on
    flag_env_var = Column(String, default="FLAG")          # env var used to inject the flag
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=now)

    instances = relationship("Instance", back_populates="challenge", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="challenge", cascade="all, delete-orphan")


class Instance(Base):
    """A live, per-user running copy of a challenge container."""
    __tablename__ = "instances"
    __table_args__ = (
        Index("ix_instances_user_challenge_status", "user_id", "challenge_id", "status"),
    )

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False, index=True)
    container_id = Column(String, nullable=False)
    host_port = Column(Integer, nullable=False)
    flag_value = Column(String, nullable=False)   # unique flag injected into this instance
    status = Column(String, default="running", index=True)     # running | stopped | expired
    started_at = Column(DateTime, default=now)
    expires_at = Column(DateTime, nullable=False, index=True)

    user = relationship("User", back_populates="instances")
    challenge = relationship("Challenge", back_populates="instances")


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        Index("ix_submissions_user_challenge_correct", "user_id", "challenge_id", "correct"),
    )

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False, index=True)
    submitted_flag = Column(String, nullable=False)
    correct = Column(Boolean, default=False, index=True)
    submitted_at = Column(DateTime, default=now, index=True)

    user = relationship("User", back_populates="submissions")
    challenge = relationship("Challenge", back_populates="submissions")

