import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.db import Base, engine, SessionLocal
from app.models import models  # noqa: F401 - ensures models are registered
from app.api import auth, challenges, instances, submissions, scoreboard
from app.services import orchestrator
from app.services.seeder import seed_challenges

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ctf-platform")

FRONTEND_DIR = (BACKEND_DIR.parent / "frontend").resolve()


async def periodic_instance_cleanup():
    """Background task to periodically reap expired container/process instances."""
    while True:
        try:
            await asyncio.sleep(settings.CLEANUP_INTERVAL_SECONDS)
            db = SessionLocal()
            try:
                cleaned = orchestrator.cleanup_expired_instances(db)
                if cleaned > 0:
                    logger.info("Reaped %d expired challenge instance(s)", cleaned)
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Error in instance cleanup loop: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized with URL: %s", settings.DATABASE_URL)

    # Automatically ensure challenge problems are loaded into the database
    db = SessionLocal()
    try:
        challenge_count = db.query(models.Challenge).count()
        if challenge_count == 0:
            logger.info("No challenges found in DB. Auto-seeding from %s...", settings.CHALLENGES_DIR)
            added, updated = seed_challenges(settings.CHALLENGES_DIR)
            logger.info("Auto-seeded %d challenges into database.", added)
        else:
            logger.info("Found %d challenge(s) in database.", challenge_count)
    except Exception as e:
        logger.error("Failed to verify/seed challenges on startup: %s", e)
    finally:
        db.close()

    # Start background cleanup task
    cleanup_task = asyncio.create_task(periodic_instance_cleanup())
    logger.info("Background instance expiry reaper started (interval=%ds)", settings.CLEANUP_INTERVAL_SECONDS)

    yield

    # Shutdown: cancel cleanup task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    logger.info("CTF Platform API shutdown complete.")


app = FastAPI(
    title="CTF Platform API",
    version="1.0.0",
    description="HackTheBox-style CTF Platform API with dynamic instances, unique flags, and scoring.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(challenges.router)
app.include_router(instances.router)
app.include_router(submissions.router)
app.include_router(scoreboard.router)


@app.get("/health")
def health():
    docker_ok = orchestrator.is_docker_available()
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "docker_available": docker_ok,
        "orchestrator_backend": "docker" if docker_ok else "process_fallback",
        "challenge_host": settings.CHALLENGE_HOST,
    }


# Mount static frontend files if directory exists
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


