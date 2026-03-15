"""
Tests for the Mergington High School Management System API.

Uses AAA pattern (Arrange-Act-Assert) for test structure.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient instance for each test."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities state before each test."""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
    })
    yield
    activities.clear()


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns the expected structure and known activities."""
        # Arrange
        expected_keys = {"Chess Club", "Programming Class", "Gym Class"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        returned_activities = response.json()
        assert set(returned_activities.keys()) == expected_keys
        assert "Chess Club" in returned_activities
        assert returned_activities["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"

    def test_get_activities_response_structure(self, client):
        """Test that activity objects have the expected structure."""
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities_data.items():
            assert set(activity_data.keys()) == expected_fields
            assert isinstance(activity_data["participants"], list)


class TestSignUpForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_adds_participant_successfully(self, client):
        """Test that signup adds a participant and returns a success message."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        # Verify participant was actually added
        assert email in activities[activity_name]["participants"]

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signup to a non-existent activity returns 404."""
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_participant_returns_400(self, client):
        """Test that attempting to signup an already-registered participant returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_successfully(self, client):
        """Test that removing a participant returns success message."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        # Verify participant was actually removed
        assert email not in activities[activity_name]["participants"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Test that removing from a non-existent activity returns 404."""
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing a non-existent participant returns 404."""
        # Arrange
        activity_name = "Programming Class"
        email = "notarealstudent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
