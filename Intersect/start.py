#!/usr/bin/env python3
"""
==============================================================================
   INTERSECT / CTF Platform - All-in-One Platform Runner
   Spawns Backend API (:8000), Frontend App (:8080), Database & Orchestrator
==============================================================================
"""
import os
import sys
import time
import signal
import subprocess
import webbrowser
import socket
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
SCRIPTS_DIR = ROOT_DIR / "scripts"
CHALLENGES_DIR = ROOT_DIR / "challenges"

VENV_DIR = BACKEND_DIR / "venv"


def get_system_python():
    """Find the best system Python executable for creating the venv."""
    if os.name == "nt":
        # On Windows, prefer standard Windows Python distributions over MSYS2/Cygwin
        candidates = [
            Path(os.path.expanduser(r"~\anaconda3\python.exe")),
            Path(os.path.expanduser(r"~\AppData\Local\Programs\Python\Python313\python.exe")),
            Path(os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\python.exe")),
            Path(os.path.expanduser(r"~\AppData\Local\Programs\Python\Python311\python.exe")),
            Path(r"C:\Python313\python.exe"),
            Path(r"C:\Python312\python.exe"),
            Path(r"C:\Python311\python.exe"),
        ]
        for c in candidates:
            if c.exists():
                return str(c)
    return sys.executable


def get_venv_python():
    candidates = [
        VENV_DIR / "Scripts" / "python.exe",
        VENV_DIR / "bin" / "python.exe",
        VENV_DIR / "bin" / "python",
    ]
    for c in candidates:
        if c.exists():
            return c
    return get_system_python()


def get_venv_pip():
    candidates = [
        VENV_DIR / "Scripts" / "pip.exe",
        VENV_DIR / "bin" / "pip.exe",
        VENV_DIR / "bin" / "pip",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None



def print_banner():
    banner = r"""
===============================================================================
    ___ _   _ _____ _____ ____  ____  _____ ____ _____ 
   |_ _| \ | |_   _| ____|  _ \/ ___|| ____/ ___|_   _|
    | ||  \| | | | |  _| | |_) \___ \|  _|| |     | |  
    | || |\  | | | | |___|  _ < ___) | |__| |___  | |  
   |___|_| \_| |_| |_____|_| \_\____/|_____\____| |_|  
                                                       
   >> HACK THE BOX STYLE CTF PLATFORM - ONLINE RANGE <<
===============================================================================
    """
    print(banner)


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def ensure_environment():
    print("[1/4] Checking Python environment and dependencies...")
    if not VENV_DIR.exists():
        sys_py = get_system_python()
        print(f"      Creating virtual environment at: {VENV_DIR} using {sys_py} ...")
        subprocess.check_call([sys_py, "-m", "venv", str(VENV_DIR)])

    py_bin = get_venv_python()

    # Install/upgrade backend requirements and flask for challenge apps
    req_file = BACKEND_DIR / "requirements.txt"
    if req_file.exists():
        print("      Verifying and installing dependencies...")
        res = subprocess.run(
            [str(py_bin), "-m", "pip", "install", "-r", str(req_file), "flask==3.0.3"],
            capture_output=True,
            text=True
        )
        if res.returncode != 0:
            print("      [!] pip installation error:")
            print(res.stderr or res.stdout)
            sys.exit(1)
    print("      Environment ready! [OK]")


def seed_database():
    print("[2/4] Seeding challenge database...")
    seed_script = SCRIPTS_DIR / "seed_db.py"
    py_bin = get_venv_python()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)
    subprocess.check_call([str(py_bin), str(seed_script)], env=env)


def check_docker():
    print("[3/4] Checking Orchestrator Backend...")
    try:
        import docker
        client = docker.from_env()
        client.ping()
        print("      Docker daemon detected! Using high-isolation container runner.")
    except Exception:
        print("      Docker daemon not reachable. Using built-in process runner fallback.")


def main():
    print_banner()

    # Step 1: Environment
    ensure_environment()

    # Step 2: Database & Seeding
    seed_database()

    # Step 3: Docker check
    check_docker()

    # Check ports
    if is_port_in_use(8000):
        print("WARNING: Port 8000 is already in use. Backend may fail to bind.")
    if is_port_in_use(8080):
        print("WARNING: Port 8080 is already in use. Frontend may fail to bind.")

    print("[4/4] Launching CTF Services...")
    processes = []
    py_bin = get_venv_python()

    # Start Backend API
    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = str(BACKEND_DIR)
    backend_cmd = [
        str(py_bin), "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    print("      Starting Backend API on http://127.0.0.1:8000 ...")
    p_backend = subprocess.Popen(backend_cmd, cwd=str(BACKEND_DIR), env=backend_env)
    processes.append(p_backend)

    # Start Frontend Server
    frontend_cmd = [
        str(py_bin), "-m", "http.server",
        "8080",
        "--directory", str(FRONTEND_DIR)
    ]

    print("      Starting Frontend UI on http://127.0.0.1:8080 ...")
    p_frontend = subprocess.Popen(frontend_cmd, cwd=str(FRONTEND_DIR))
    processes.append(p_frontend)

    time.sleep(1.5)
    try:
        webbrowser.open("http://localhost:8080")
    except Exception:
        pass

    print("\n" + "=" * 79)
    print("  >> PLATFORM IS LIVE AND READY!")
    print("  - Frontend Application : http://localhost:8080")
    print("  - Backend API Docs     : http://localhost:8000/docs")
    print("  - Health Check Endpoint: http://localhost:8000/health")
    print("=" * 79)
    print("  Press Ctrl+C at any time to gracefully stop all services.\n")

    def shutdown(signum, frame):
        print("\nStopping CTF Platform services...")
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        for p in processes:
            try:
                p.wait(timeout=3)
            except Exception:
                p.kill()
        print("All services stopped. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Keep alive
    try:
        while True:
            for p in processes:
                if p.poll() is not None:
                    print(f"Process {p.args} exited unexpectedly with code {p.returncode}")
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()
