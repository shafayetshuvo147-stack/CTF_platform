import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_full_platform_flow():
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    print("\n[TEST 1] /health -> 200 OK")

    # 2. Challenges list
    res = client.get("/challenges/")
    chals = res.json()
    assert res.status_code == 200
    assert len(chals) == 101
    print(f"[TEST 2] /challenges/ -> 200 OK (Loaded {len(chals)} challenges)")

    # 3. Static root serving
    res = client.get("/")
    assert res.status_code == 200
    assert "INTERSECT" in res.text
    print("[TEST 3] / (Frontend Index HTML) -> 200 OK")

    # 4. Static app.js serving
    res = client.get("/app.js")
    assert res.status_code == 200
    assert "EMBEDDED_CHALLENGES" in res.text
    print("[TEST 4] /app.js -> 200 OK")

    # 5. Auth register & login
    user = "TestOperative_02"
    email = "op02@example.com"
    pwd = "Password123!"
    try:
        client.post("/auth/register", json={"username": user, "email": email, "password": pwd})
    except Exception:
        pass

    res = client.post("/auth/login", data={"username": user, "password": pwd})
    assert res.status_code == 200
    token = res.json()["access_token"]
    print("[TEST 5] Register & Login -> 200 OK")

    # 6. Start instance
    headers = {"Authorization": f"Bearer {token}"}
    target_chal = chals[0]
    chal_name = target_chal["name"]
    chal_id = target_chal["id"]
    print(f"[TEST 6] Starting instance for {chal_name}...")
    res = client.post(f"/instances/{chal_id}/start", headers=headers)
    assert res.status_code == 200
    inst_data = res.json()
    assert "id" in inst_data
    print(f"[TEST 6] Instance started at {inst_data.get('connect_info')}")

    # 7. Check instance in /instances/mine
    res = client.get("/instances/mine", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1
    print(f"[TEST 7] /instances/mine -> {len(res.json())} active instance(s)")

    # 8. Stop instance
    res = client.post(f"/instances/{inst_data['id']}/stop", headers=headers)
    assert res.status_code == 200
    print("[TEST 8] Stop instance -> 200 OK")

    print("\nALL PLATFORM TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_full_platform_flow()
