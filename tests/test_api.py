from fastapi.testclient import TestClient
from agent_reliability.api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_missing_evaluation_returns_404():
    response = client.get("/evaluations/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Evaluation attempt not found"


def test_create_evaluation_rejects_missing_field():
    response = client.post(
        "/evaluations",
        json={"task_id": "refund_eligible_001"},
    )
    assert response.status_code == 422


def test_create_evaluation_rejects_unsupported_agent():
    response = client.post(
        "/evaluations",
        json={"task_id": "refund_eligible_001", "agent_id": "unknown_bot"},
    )
    assert response.status_code == 400
    assert "Unsupported agent_id" in response.json()["detail"]


def test_create_and_read_broken_agent_evaluation():
    # 1. Run the broken agent via POST
    post_response = client.post(
        "/evaluations",
        json={
            "task_id": "refund_eligible_001",
            "agent_id": "broken_scripted",
        },
    )
    assert post_response.status_code == 201

    data = post_response.json()
    assert data["evaluation_result"]["passed"] is False
    assert data["trace_events"] == []

    attempt_id = data["attempt_id"]

    get_response = client.get(f"/evaluations/{attempt_id}")
    assert get_response.status_code == 200
    assert get_response.json()["attempt_id"] == attempt_id
