import copy
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_root_redirects_to_index():
    # Arrange

    # Act
    resp = client.get("/", allow_redirects=False)

    # Assert
    assert resp.status_code == 307
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities_aaa():
    # Arrange

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_then_duplicate_then_unregister_aaa():
    # Arrange
    activity = "Chess Club"
    email = "pytest-student@example.edu"
    snapshot = copy.deepcopy(activities)

    try:
        # Act - signup
        resp_signup = client.post(f"/activities/{activity}/signup?email={email}")
        # Assert - signup succeeded
        assert resp_signup.status_code == 200
        assert resp_signup.json()["message"] == f"Signed up {email} for {activity}"
        assert email in activities[activity]["participants"]

        # Act - duplicate signup
        resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
        # Assert - duplicate blocked
        assert resp_dup.status_code == 400

        # Act - unregister
        resp_unreg = client.delete(f"/activities/{activity}/signup?email={email}")
        # Assert - unregistered
        assert resp_unreg.status_code == 200
        assert resp_unreg.json()["message"] == f"Unregistered {email} from {activity}"

        # Act - unregister again
        resp_unreg_again = client.delete(f"/activities/{activity}/signup?email={email}")
        # Assert - not found
        assert resp_unreg_again.status_code == 404

    finally:
        activities.clear()
        activities.update(snapshot)


def test_signup_for_nonexistent_activity_aaa():
    # Arrange
    activity = "Nonexistent Club"
    email = "noone@example.edu"

    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 404


def test_unregister_when_not_signed_up_aaa():
    # Arrange
    activity = "Programming Class"
    email = "not-signed@example.edu"
    snapshot = copy.deepcopy(activities)

    try:
        # Ensure the email is not in participants
        if email in activities[activity]["participants"]:
            activities[activity]["participants"].remove(email)

        # Act
        resp = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert resp.status_code == 404

    finally:
        activities.clear()
        activities.update(snapshot)
