import copy
from fastapi.testclient import TestClient

from src import app as application
from src.app import activities


client = TestClient(application.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_and_unregister():
    # Arrange - snapshot
    snapshot = copy.deepcopy(activities)
    activity = "Chess Club"
    email = "pytest-student@example.edu"

    try:
        # Act - signup
        resp = client.post(f"/activities/{activity}/signup?email={email}")
        assert resp.status_code == 200
        assert resp.json()["message"] == f"Signed up {email} for {activity}"

        # Assert participant added
        assert email in activities[activity]["participants"]

        # Act - duplicate signup
        resp2 = client.post(f"/activities/{activity}/signup?email={email}")
        # Should return 400 for duplicate
        assert resp2.status_code == 400

        # Act - unregister
        resp3 = client.delete(f"/activities/{activity}/signup?email={email}")
        assert resp3.status_code == 200
        assert resp3.json()["message"] == f"Unregistered {email} from {activity}"

        # Act - unregister again should 404
        resp4 = client.delete(f"/activities/{activity}/signup?email={email}")
        assert resp4.status_code == 404

    finally:
        # Restore
        activities.clear()
        activities.update(snapshot)
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_data():
    # Arrange
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_duplicate_block():
    # Arrange
    activity = "Chess Club"
    email = "teststudent@example.edu"
    original = list(activities[activity]["participants"])  # snapshot

    try:
        # Act: first signup should succeed
        resp1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert resp1.status_code == 200
        assert email in activities[activity]["participants"]

        # Act: second signup should be blocked
        resp2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert resp2.status_code == 400
        body = resp2.json()
        assert "already signed up" in body.get("detail", "")

    finally:
        # Teardown: restore original participants
        activities[activity]["participants"] = original


def test_unregister_endpoint():
    # Arrange
    activity = "Programming Class"
    email = "unregister-test@example.edu"
    original = list(activities[activity]["participants"])  # snapshot

    try:
        # Ensure signup exists
        resp_signup = client.post(f"/activities/{activity}/signup?email={email}")
        assert resp_signup.status_code == 200
        assert email in activities[activity]["participants"]

        # Act: unregister
        resp_unreg = client.delete(f"/activities/{activity}/signup?email={email}")
        assert resp_unreg.status_code == 200
        assert email not in activities[activity]["participants"]

    finally:
        # Teardown
        activities[activity]["participants"] = original
