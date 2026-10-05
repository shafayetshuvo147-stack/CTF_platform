"""
Automated Test Suite for the CTF Platform Backend.
Tests authentication, challenges, instances, submissions, dynamic scoring, and scoreboard.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ["CTF_DATABASE_URL"] = "sqlite:///./test_ctf.db"
os.environ["CTF_ORCHESTRATOR"] = "process"
os.environ["CTF_CHALLENGES_DIR"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "challenges"))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app
from app.core.db import Base, engine, SessionLocal
from app.models.models import Challenge, User, Instance, Submission
from scripts.seed_db import seed_challenges

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_challenges(os.environ["CTF_CHALLENGES_DIR"])
    yield
    # Cleanup test db
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_ctf.db"):
        try:
            os.remove("./test_ctf.db")
        except Exception:
            pass


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "orchestrator_backend" in data


def test_user_registration_and_login():
    # 1. Register User A (HackerOne)
    reg_resp = client.post("/auth/register", json={
        "username": "HackerOne",
        "email": "hacker1@example.com",
        "password": "SuperSecretPassword123!"
    })
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["username"] == "HackerOne"
    assert "id" in user_data

    # 2. Duplicate registration should fail
    dup_resp = client.post("/auth/register", json={
        "username": "HackerOne",
        "email": "diff@example.com",
        "password": "Password123!"
    })
    assert dup_resp.status_code == 400

    # 3. Login
    login_resp = client.post("/auth/login", data={
        "username": "HackerOne",
        "password": "SuperSecretPassword123!"
    })
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 4. Profile endpoint /auth/me
    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    profile = me_resp.json()
    assert profile["username"] == "HackerOne"
    assert profile["score"] == 0
    assert profile["solves_count"] == 0


def test_challenges_list_and_404():
    response = client.get("/challenges/")
    assert response.status_code == 200
    chals = response.json()
    assert len(chals) >= 3

    chal_id = chals[0]["id"]
    single_resp = client.get(f"/challenges/{chal_id}")
    assert single_resp.status_code == 200
    assert single_resp.json()["id"] == chal_id

    # Non-existent challenge returns 404
    bad_resp = client.get("/challenges/non-existent-uuid")
    assert bad_resp.status_code == 404


def test_instance_start_stop_and_submission_flow():
    # Register & login player
    client.post("/auth/register", json={
        "username": "CyberNinja",
        "email": "ninja@example.com",
        "password": "NinjaPassword123!"
    })
    login_res = client.post("/auth/login", data={
        "username": "CyberNinja",
        "password": "NinjaPassword123!"
    })
    token = login_res.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Get challenges
    chals = client.get("/challenges/").json()
    sqli_chal = next(c for c in chals if c["slug"] == "web-sqli-101")

    # Start instance
    start_resp = client.post(f"/instances/{sqli_chal['id']}/start", headers=auth_headers)
    assert start_resp.status_code == 200
    inst_data = start_resp.json()
    assert inst_data["challenge_id"] == sqli_chal["id"]
    assert "host_port" in inst_data
    assert "connect_info" in inst_data

    # Starting again should return existing running instance
    start_again_resp = client.post(f"/instances/{sqli_chal['id']}/start", headers=auth_headers)
    assert start_again_resp.status_code == 200
    assert start_again_resp.json()["id"] == inst_data["id"]

    # Check my instances
    mine_resp = client.get("/instances/mine", headers=auth_headers)
    assert mine_resp.status_code == 200
    mine = mine_resp.json()
    assert len(mine) >= 1

    # Get the flag from DB for testing verification
    db = SessionLocal()
    db_inst = db.query(Instance).filter(Instance.id == inst_data["id"]).first()
    flag_val = db_inst.flag_value
    db.close()

    # 1. Submit incorrect flag
    sub_wrong = client.post("/submissions/", json={
        "challenge_id": sqli_chal["id"],
        "flag": "CTF{completely_wrong_flag}"
    }, headers=auth_headers)
    assert sub_wrong.status_code == 200
    assert sub_wrong.json()["correct"] is False

    # 2. Submit correct flag
    sub_correct = client.post("/submissions/", json={
        "challenge_id": sqli_chal["id"],
        "flag": flag_val
    }, headers=auth_headers)
    assert sub_correct.status_code == 200
    assert sub_correct.json()["correct"] is True
    assert sub_correct.json()["points_awarded"] > 0

    # 3. Submit again -> Already solved
    sub_dup = client.post("/submissions/", json={
        "challenge_id": sqli_chal["id"],
        "flag": flag_val
    }, headers=auth_headers)
    assert sub_dup.status_code == 200
    assert sub_dup.json()["correct"] is False
    assert "already solved" in sub_dup.json()["message"].lower()

    # 4. Check submission history
    hist_resp = client.get("/submissions/mine", headers=auth_headers)
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) >= 2

    # 5. Stop instance
    stop_resp = client.post(f"/instances/{inst_data['id']}/stop", headers=auth_headers)
    assert stop_resp.status_code == 200

    # 6. Check scoreboard
    board_resp = client.get("/scoreboard/")
    assert board_resp.status_code == 200
    board = board_resp.json()
    assert len(board) >= 1
    ninja_entry = next(b for b in board if b["username"] == "CyberNinja")
    assert ninja_entry["solves"] == 1
    assert ninja_entry["score"] > 0


def test_all_challenge_categories_seeded():
    response = client.get("/challenges/")
    assert response.status_code == 200
    chals = response.json()
    slugs = {c["slug"] for c in chals}
    categories = {c["category"] for c in chals}

    assert "crypto-caesar-vault" in slugs
    assert "web-headers-leak" in slugs
    assert "web-sqli-101" in slugs
    assert "web-ping-diagnostic" in slugs
    assert "forensics-log-audit" in slugs
    assert "rev-matrix-vault" in slugs

    assert "web" in categories
    assert "crypto" in categories
    assert "forensics" in categories
    assert "rev" in categories


def test_multi_user_scoring_and_decay():
    # Register Player 1 and Player 2
    for user_name in ["PlayerOne", "PlayerTwo"]:
        client.post("/auth/register", json={
            "username": user_name,
            "email": f"{user_name.lower()}@example.com",
            "password": "Password123!"
        })

    token1 = client.post("/auth/login", data={"username": "PlayerOne", "password": "Password123!"}).json()["access_token"]
    token2 = client.post("/auth/login", data={"username": "PlayerTwo", "password": "Password123!"}).json()["access_token"]

    chals = client.get("/challenges/").json()
    target_chal = next(c for c in chals if c["slug"] == "crypto-caesar-vault")

    # Start instance for Player 1
    inst1 = client.post(f"/instances/{target_chal['id']}/start", headers={"Authorization": f"Bearer {token1}"}).json()
    db = SessionLocal()
    flag1 = db.query(Instance).filter(Instance.id == inst1["id"]).first().flag_value
    db.close()

    # Player 1 solves
    res1 = client.post("/submissions/", json={"challenge_id": target_chal["id"], "flag": flag1}, headers={"Authorization": f"Bearer {token1}"}).json()
    assert res1["correct"] is True
    first_solve_points = res1["points_awarded"]

    # Start instance for Player 2
    inst2 = client.post(f"/instances/{target_chal['id']}/start", headers={"Authorization": f"Bearer {token2}"}).json()
    db = SessionLocal()
    flag2 = db.query(Instance).filter(Instance.id == inst2["id"]).first().flag_value
    db.close()

    # Player 2 solves
    res2 = client.post("/submissions/", json={"challenge_id": target_chal["id"], "flag": flag2}, headers={"Authorization": f"Bearer {token2}"}).json()
    assert res2["correct"] is True

    # Check updated challenge points (should have decayed slightly or remained within bounds)
    updated_chal = client.get(f"/challenges/{target_chal['id']}").json()
    assert updated_chal["solves_count"] >= 2
    assert updated_chal["points"] <= target_chal["points"]

