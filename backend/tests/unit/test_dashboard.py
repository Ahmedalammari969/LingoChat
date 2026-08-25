"""
LinguaChat — Dashboard Stats API Unit Tests
Tests for TASK-06-YOUSEF
Contract: docs/api-contract.md § 7
"""

import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.database.models.user import User
from app.core.security import create_access_token
from app.dashboard import service as dashboard_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    u_id = uuid.uuid4()
    return User(
        id=u_id,
        username="dash_user",
        hashed_password="hashed_password",
        preferred_language="ar",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=True,
    )


@pytest.fixture
def auth_header(test_user):
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


def test_get_dashboard_stats_success(client, test_user, auth_header):
    """Test authenticated request returns 200 OK with all 5 required metric fields."""
    mock_stats = {
        "total_users": 15,
        "total_rooms": 4,
        "total_messages": 120,
        "total_translations": 230,
        "active_connections": 3,
    }

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.dashboard.service.get_system_stats", new_callable=AsyncMock) as mock_get_stats:

        mock_get_user.return_value = test_user
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/v1/dashboard/stats", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert data["total_users"] == 15
        assert data["total_rooms"] == 4
        assert data["total_messages"] == 120
        assert data["total_translations"] == 230
        assert data["active_connections"] == 3


def test_get_dashboard_stats_unauthorized_without_token(client):
    """Test accessing dashboard stats without token returns 401 Unauthorized."""
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 401


def test_get_dashboard_stats_empty_database(client, test_user, auth_header):
    """Test dashboard stats with empty database returns zero for all fields."""
    mock_stats = {
        "total_users": 0,
        "total_rooms": 0,
        "total_messages": 0,
        "total_translations": 0,
        "active_connections": 0,
    }

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.dashboard.service.get_system_stats", new_callable=AsyncMock) as mock_get_stats:

        mock_get_user.return_value = test_user
        mock_get_stats.return_value = mock_stats

        response = client.get("/api/v1/dashboard/stats", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert data["total_users"] == 0
        assert data["total_rooms"] == 0
        assert data["total_messages"] == 0
        assert data["total_translations"] == 0
        assert data["active_connections"] == 0
