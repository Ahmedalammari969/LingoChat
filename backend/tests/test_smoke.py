"""
LinguaChat — Smoke Test

Verifies that the FastAPI application starts and the health endpoint responds.
This is the only test that can run without a database or external services.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """
    SMOKE TEST: Verify the /health endpoint returns 200 OK.
    This test confirms the FastAPI application initializes correctly.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_unknown_route_returns_404():
    """Verify that unknown routes return 404."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/nonexistent-route-xyz")

    assert response.status_code == 404
