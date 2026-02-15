"""Tests for the API client."""

import pytest
import responses

from nodie_cli.client import NodieClient, APIError


@pytest.fixture
def client():
    """Create a test client."""
    return NodieClient(token="test_token")


@responses.activate
def test_login_success(client):
    """Test successful login."""
    responses.add(
        responses.POST,
        "https://nodie.host/api/auth/login",
        json={"token": "new_token", "user": {"id": "123"}},
        status=200,
    )
    
    result = client.login("test@example.com", "password")
    assert result["token"] == "new_token"


@responses.activate
def test_login_failure(client):
    """Test login failure."""
    responses.add(
        responses.POST,
        "https://nodie.host/api/auth/login",
        json={"detail": "Invalid credentials"},
        status=401,
    )
    
    with pytest.raises(APIError) as exc_info:
        client.login("test@example.com", "wrong_password")
    
    assert "Invalid credentials" in str(exc_info.value)


@responses.activate
def test_get_me(client):
    """Test getting current user."""
    responses.add(
        responses.GET,
        "https://nodie.host/api/auth/me",
        json={"id": "123", "username": "testuser", "totalPoints": 100.5},
        status=200,
    )
    
    result = client.get_me()
    assert result["username"] == "testuser"
    assert result["totalPoints"] == 100.5


@responses.activate
def test_register_node(client):
    """Test node registration."""
    responses.add(
        responses.POST,
        "https://nodie.host/api/node/register",
        json={"id": "node_123", "status": "online"},
        status=200,
    )
    
    result = client.register_node("device_abc", "1.2.3.4")
    assert result["id"] == "node_123"


@responses.activate
def test_send_heartbeat(client):
    """Test sending heartbeat."""
    responses.add(
        responses.POST,
        "https://nodie.host/api/node/heartbeat",
        json={"pointsEarned": 0.5, "networkScore": 85},
        status=200,
    )
    
    result = client.send_heartbeat(
        node_id="node_123",
        bandwidth_used=0.1,
        speed_mbps=50.0,
    )
    assert result["pointsEarned"] == 0.5


@responses.activate
def test_connection_error():
    """Test handling connection errors."""
    responses.add(
        responses.GET,
        "https://nodie.host/api/auth/me",
        body=ConnectionError("Network error"),
    )
    
    client = NodieClient(token="test")
    
    with pytest.raises(APIError) as exc_info:
        client.get_me()
    
    assert "Connection failed" in str(exc_info.value)
