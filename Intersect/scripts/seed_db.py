import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.config import settings
from app.services.seeder import seed_challenges


def main():
    print("=== CTF Challenge Database Seeder ===")
    print(f"Target Database:   {settings.DATABASE_URL}")
    print(f"Challenges Folder: {settings.CHALLENGES_DIR}")
    added, updated = seed_challenges(settings.CHALLENGES_DIR)
    print(f"Seeding complete! Added: {added}, Updated: {updated}\n")


if __name__ == "__main__":
    main()


