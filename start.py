#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

PLATFORM_DIR = Path(__file__).resolve().parent / "ctf-platform"
START_SCRIPT = PLATFORM_DIR / "start.py"

if __name__ == "__main__":
    os.chdir(str(PLATFORM_DIR))
    sys.exit(subprocess.call([sys.executable, str(START_SCRIPT)]))
