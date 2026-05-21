import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for testing the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    original = {
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
        "Basketball Team": {
            "description": "Practice team basketball skills and play in interschool games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["nina@mergington.edu", "alex@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Train for soccer matches and build teamwork on the field",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["maria@mergington.edu", "leon@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and creative crafts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["lily@mergington.edu", "noah@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Practice instruments and perform musical pieces together",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "jack@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Prepare for science competitions and solve challenging problems",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["sophia@mergington.edu", "maya@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking skills and compete in debate tournaments",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["ethan@mergington.edu", "zoe@mergington.edu"]
        }
    }
    
    activities.clear()
    activities.update(original)
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        assert len(activities_data) == 9
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
    
    def test_activity_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        activities_data = response.json()
        
        activity = activities_data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_participants_list(self, client):
        """Test that participants list contains correct data"""
        response = client.get("/activities")
        activities_data = response.json()
        
        chess_club = activities_data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful participant signup"""
        response = client.post(
            "/activities/Chess Club/signup?email=newemail@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "newemail@mergington.edu" in result["message"]
    
    def test_participant_added_to_activity(self, client):
        """Test that participant is actually added to the activity"""
        email = "newemail@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert email in chess_club["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]
    
    def test_duplicate_signup(self, client):
        """Test attempting to sign up same participant twice"""
        email = "michael@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 400
        
        # Second signup should fail with 400
        result1 = response1.json()
        assert "already signed up" in result1["detail"]
    
    def test_signup_updates_spots_left(self, client):
        """Test that available spots are reduced after signup"""
        response_before = client.get("/activities")
        chess_before = response_before.json()["Chess Club"]
        spots_before = chess_before["max_participants"] - len(chess_before["participants"])
        
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        response_after = client.get("/activities")
        chess_after = response_after.json()["Chess Club"]
        spots_after = chess_after["max_participants"] - len(chess_after["participants"])
        
        assert spots_after == spots_before - 1


class TestDeleteSignupEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_successful_deletion(self, client):
        """Test successful participant deletion"""
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "Unregistered" in result["message"]
    
    def test_participant_removed_from_activity(self, client):
        """Test that participant is actually removed from the activity"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess Club/signup?email={email}")
        
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert email not in chess_club["participants"]
    
    def test_delete_from_nonexistent_activity(self, client):
        """Test deletion from activity that doesn't exist"""
        response = client.delete(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]
    
    def test_delete_nonexistent_participant(self, client):
        """Test deletion of participant not in activity"""
        response = client.delete(
            "/activities/Chess Club/signup?email=notamember@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "not signed up" in result["detail"]
    
    def test_deletion_updates_spots_available(self, client):
        """Test that available spots are increased after deletion"""
        response_before = client.get("/activities")
        chess_before = response_before.json()["Chess Club"]
        spots_before = chess_before["max_participants"] - len(chess_before["participants"])
        
        client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        
        response_after = client.get("/activities")
        chess_after = response_after.json()["Chess Club"]
        spots_after = chess_after["max_participants"] - len(chess_after["participants"])
        
        assert spots_after == spots_before + 1


class TestIntegration:
    """Integration tests for signup and deletion workflows"""
    
    def test_signup_then_delete_workflow(self, client):
        """Test complete workflow: signup, verify, delete, verify"""
        email = "testuser@mergington.edu"
        activity = "Chess Club"
        
        # Signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Verify signup
        response2 = client.get("/activities")
        assert email in response2.json()[activity]["participants"]
        
        # Delete
        response3 = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response3.status_code == 200
        
        # Verify deletion
        response4 = client.get("/activities")
        assert email not in response4.json()[activity]["participants"]
    
    def test_multiple_signups(self, client):
        """Test multiple participants signing up for the same activity"""
        activity = "Programming Class"
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        for email in emails:
            assert email in participants
