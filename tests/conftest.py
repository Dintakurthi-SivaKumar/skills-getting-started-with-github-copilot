import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for testing the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_activities_backup():
    """Backup and restore activities state between tests"""
    # Store original activities
    original = {k: {**v, "participants": v["participants"].copy()} for k, v in activities.items()}
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original)
