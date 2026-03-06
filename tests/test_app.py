import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Test cases for GET /activities endpoint."""

    def test_get_activities_success(self, client):
        # Arrange
        # (TestClient and app setup handled by fixture)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # All activities loaded

        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        assert chess_club["max_participants"] == 12


class TestSignup:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        # Arrange
        email = "new_student@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity}" == data["message"]

        # Verify participant was added
        response_check = client.get("/activities")
        activities = response_check.json()
        assert email in activities[activity]["participants"]

    def test_signup_duplicate(self, client):
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Programming Class"

        # First signup (should succeed)
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act - Try to signup again
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up" == data["detail"]

    def test_signup_invalid_activity(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "NonExistent Activity"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" == data["detail"]


class TestDeleteSignup:
    """Test cases for DELETE /activities/{activity_name}/signup endpoint."""

    def test_delete_success(self, client):
        # Arrange
        email = "remove_me@mergington.edu"
        activity = "Gym Class"

        # First add the participant
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Removed {email} from {activity}" == data["message"]

        # Verify participant was removed
        response_check = client.get("/activities")
        activities = response_check.json()
        assert email not in activities[activity]["participants"]

    def test_delete_not_signed_up(self, client):
        # Arrange
        email = "not_signed@mergington.edu"
        activity = "Tennis Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Student not signed up for this activity" == data["detail"]

    def test_delete_invalid_activity(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "InvalidActivity"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" == data["detail"]