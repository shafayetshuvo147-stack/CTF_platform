# CTF Platform

A minimal, working HackTheBox-style CTF platform: dynamic per-user challenge
instances, unique flags per instance, submission validation, and a scoreboard
with decaying dynamic scoring.

This is a functional starting scaffold, not a production system — see
"Hardening before production" below.

## Quick start (local dev)

1. **Build the example challenge image**
   ```bash
   cd scripts
   chmod +x build_all_challenges.sh
   ./build_all_challenges.sh
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   python ../scripts/seed_db.py     # registers challenges from challenges/*/challenge.yaml
   uvicorn app.main:app --reload
   ```
   The backend needs access to the Docker socket to launch challenge
   containers (it uses the `docker` Python SDK against your local daemon).

3. **Open the frontend**
   Serve `frontend/` with any static server, e.g.:
   ```bash
   cd frontend
   python3 -m http.server 8080
   ```
   Then open `http://localhost:8080`. It's a full app — register/login screen,
   dashboard, browsable case-file grid with search and category filters, a
   challenge modal with a live boot sequence + countdown timer + flag
   submission, a scoreboard, and a profile page. It talks to the API at
   `http://localhost:8000` by default; override by setting
   `window.CTF_API_BASE` before `app.js` loads if you deploy the API
   elsewhere.

## Or run everything with Docker Compose

```bash
cd infra
docker compose -f docker-compose.platform.yml up --build
```

## Adding a new challenge

1. Create `challenges/<slug>/` with a `Dockerfile` and a `challenge.yaml`
   (see `challenges/web-sqli-101/` for the pattern).
2. The challenge's app must read its flag from an environment variable
   (default name `FLAG`) — never hardcode flags into the image.
3. Run `build_all_challenges.sh` then `seed_db.py` again.

## Architecture notes

- **Unique flags per instance**: each user gets their own container with a
  freshly generated flag injected at boot, so a leaked flag doesn't help
  other players and can be traced back to whoever leaked it.
- **Orchestrator is swappable**: `backend/app/services/orchestrator.py` talks
  to a local Docker daemon. For real multi-tenant scale, replace its
  internals with a Kubernetes client that creates a Job + NetworkPolicy per
  instance — the API layer (`instances.py`) doesn't need to change.
- **Auto-expiry**: instances carry an `expires_at`. Add a periodic worker
  (cron, Celery beat, or a k8s CronJob) that calls `orchestrator.stop_instance`
  for anything past expiry — not included here to keep the scaffold minimal.

## Known-good dependency pin

`passlib[bcrypt]` alone can resolve to a `bcrypt` release that breaks
passlib's internal self-test (`password cannot be longer than 72 bytes`)
on registration. `requirements.txt` pins `bcrypt==4.0.1` explicitly to
avoid this — keep that pin if you upgrade other dependencies.

## Hardening before production

- Put a constrained proxy (e.g. `docker-socket-proxy`) or a Kubernetes API
  in front of container orchestration — never expose the raw Docker socket
  to a network-facing service in production.
- Move off SQLite to Postgres (`CTF_DATABASE_URL`).
- Add per-user rate limiting on `/submissions/` and `/instances/*/start`.
- Add real network isolation between challenge instances (Kubernetes
  NetworkPolicies, or per-tenant Docker networks with `internal: true`).
- Consider a VPN (WireGuard/OpenVPN) per user/team for challenges that need
  raw TCP access rather than exposed host ports, as HTB does.
- Add CSRF protection and move the frontend behind proper auth/session
  handling if you build it out past this static prototype.
