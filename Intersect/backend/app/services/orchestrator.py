"""
Orchestrator service: responsible for starting/stopping isolated challenge
instances. Supports Docker container orchestration as well as a local
process-based fallback runner for local development and testing.
"""
import os
import sys
import socket
import contextlib
import subprocess
import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)

_docker_client = None
_running_processes: Dict[str, subprocess.Popen] = {}


def _get_docker_client():
    """Lazily connect to the Docker daemon."""
    global _docker_client
    if _docker_client is None:
        try:
            import docker
            client = docker.from_env()
            client.ping()
            _docker_client = client
        except Exception as e:
            logger.warning("Docker daemon not reachable: %s", e)
            _docker_client = None
    return _docker_client


def is_docker_available() -> bool:
    if settings.ORCHESTRATOR_BACKEND.lower() in ("process", "mock", "local"):
        return False
    return _get_docker_client() is not None


def _find_free_host_port(used_ports: set[int] = None) -> int:
    """Grab an available host port in our configured range."""
    used_ports = used_ports or set()
    for port in range(settings.PORT_RANGE_START, settings.PORT_RANGE_END):
        if port in used_ports:
            continue
        try:
            with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                return port
        except OSError:
            continue
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="No free ports available in configured range. Please try again later."
    )


def ensure_network():
    """Make sure the isolated bridge network for challenge containers exists."""
    client = _get_docker_client()
    if client:
        try:
            client.networks.get(settings.CHALLENGE_NETWORK)
        except Exception:
            try:
                client.networks.create(settings.CHALLENGE_NETWORK, driver="bridge", internal=False)
            except Exception as e:
                logger.warning("Could not create docker network: %s", e)


def _start_docker_instance(
    docker_image: str,
    container_port: int,
    flag_env_var: str,
    flag_value: str,
    user_id: str,
    host_port: int,
) -> dict:
    client = _get_docker_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Docker daemon is not reachable on host."
        )

    ensure_network()
    clean_tag = re.sub(r'[^a-zA-Z0-9_.-]', '-', docker_image.split('/')[-1])
    container_name = f"ctf-{user_id[:8]}-{clean_tag}-{host_port}"

    try:
        container = client.containers.run(
            docker_image,
            detach=True,
            environment={flag_env_var: flag_value},
            ports={f"{container_port}/tcp": ("0.0.0.0", host_port)},
            network=settings.CHALLENGE_NETWORK,
            cap_drop=["ALL"],
            security_opt=["no-new-privileges"],
            mem_limit="256m",
            pids_limit=128,
            labels={"ctf.user_id": user_id, "ctf.managed": "true"},
            auto_remove=False,
            name=container_name,
        )
        return {"container_id": f"docker:{container.id}", "host_port": host_port}
    except Exception as e:
        logger.error("Failed to run Docker container: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start challenge container ({docker_image}): {str(e)}"
        )


def _start_process_instance(
    slug: str,
    flag_env_var: str,
    flag_value: str,
    user_id: str,
    host_port: int,
) -> dict:
    """Fallback runner for challenges that have an app.py in challenges/<slug>/."""
    chal_dir = os.path.abspath(os.path.join(settings.CHALLENGES_DIR, slug))
    app_py = os.path.join(chal_dir, "app.py")

    env = os.environ.copy()
    env[flag_env_var] = flag_value
    env["PORT"] = str(host_port)
    env["HOST"] = "0.0.0.0"

    proc_id = f"proc:{slug}:{user_id[:8]}:{host_port}"

    if os.path.isfile(app_py):
        # We start python app with dynamic port
        wrapper_code = f"""
import os, sys
os.environ['PORT'] = '{host_port}'
os.environ['{flag_env_var}'] = '''{flag_value}'''
sys.path.insert(0, r'{chal_dir}')
import app
if hasattr(app, 'app'):
    app.app.run(host='0.0.0.0', port={host_port})
"""
        proc = subprocess.Popen(
            [sys.executable, "-c", wrapper_code],
            cwd=chal_dir,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        # Generic mock service runner responding with banner and challenge info
        mock_code = f"""
import http.server, socketserver, os
FLAG = '''{flag_value}'''
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f'<h1>CTF Challenge Instance: {slug}</h1><p>Flag is injected in environment.</p><p>Flag: {{FLAG}}</p>'
        self.wfile.write(html.encode())
with socketserver.TCPServer(('0.0.0.0', {host_port}), Handler) as httpd:
    httpd.serve_forever()
"""
        proc = subprocess.Popen(
            [sys.executable, "-c", mock_code],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    _running_processes[proc_id] = proc
    return {"container_id": proc_id, "host_port": host_port}


def start_instance(
    slug: str,
    docker_image: str,
    container_port: int,
    flag_env_var: str,
    flag_value: str,
    user_id: str,
    active_ports: set[int] = None,
) -> dict:
    """
    Starts an isolated container/process for this user with the flag injected.
    """
    host_port = _find_free_host_port(active_ports)

    if is_docker_available():
        try:
            return _start_docker_instance(
                docker_image=docker_image,
                container_port=container_port,
                flag_env_var=flag_env_var,
                flag_value=flag_value,
                user_id=user_id,
                host_port=host_port,
            )
        except Exception as e:
            logger.warning("Docker start failed, falling back to process runner: %s", e)

    return _start_process_instance(
        slug=slug,
        flag_env_var=flag_env_var,
        flag_value=flag_value,
        user_id=user_id,
        host_port=host_port,
    )


def stop_instance(container_id: str) -> None:
    if not container_id:
        return

    if container_id.startswith("docker:"):
        raw_id = container_id[len("docker:"):]
        client = _get_docker_client()
        if client:
            try:
                container = client.containers.get(raw_id)
                container.stop(timeout=3)
                container.remove(force=True)
            except Exception:
                pass
    elif container_id.startswith("proc:"):
        proc = _running_processes.pop(container_id, None)
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
    else:
        # Legacy container id string without prefix
        client = _get_docker_client()
        if client:
            try:
                container = client.containers.get(container_id)
                container.stop(timeout=3)
                container.remove(force=True)
            except Exception:
                pass


def is_running(container_id: str) -> bool:
    if not container_id:
        return False

    if container_id.startswith("docker:"):
        raw_id = container_id[len("docker:"):]
        client = _get_docker_client()
        if not client:
            return False
        try:
            container = client.containers.get(raw_id)
            return container.status == "running"
        except Exception:
            return False
    elif container_id.startswith("proc:"):
        proc = _running_processes.get(container_id)
        if proc is None:
            return False
        return proc.poll() is None
    else:
        client = _get_docker_client()
        if not client:
            return False
        try:
            container = client.containers.get(container_id)
            return container.status == "running"
        except Exception:
            return False


def cleanup_expired_instances(db: Session) -> int:
    """
    Finds running instances past their expiration time, terminates them,
    and updates their status in the database.
    """
    from app.models.models import Instance

    now_utc = datetime.now(timezone.utc)
    running_instances = (
        db.query(Instance)
        .filter(Instance.status == "running")
        .all()
    )

    cleaned_count = 0
    for inst in running_instances:
        exp = inst.expires_at
        if exp is not None:
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            else:
                exp = exp.astimezone(timezone.utc)
            if exp <= now_utc:
                try:
                    stop_instance(inst.container_id)
                except Exception as e:
                    logger.warning("Error stopping expired instance %s: %s", inst.id, e)
                inst.status = "expired"
                cleaned_count += 1

    if cleaned_count > 0:
        db.commit()

    return cleaned_count

