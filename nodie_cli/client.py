"""
HTTP client for Nodie API.
"""

import platform
import uuid
from typing import Any, Dict, Optional

import requests

from nodie_cli import __version__
from nodie_cli.config import get_config_value


class NodieClient:
    """HTTP client for communicating with the Nodie API."""
    
    def __init__(self, token: Optional[str] = None):
        self.base_url = get_config_value("api_url", "https://nodie.host/api")
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": f"nodie-cli/{__version__} ({platform.system()})",
        })
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
    
    def set_token(self, token: str) -> None:
        """Set the authentication token."""
        self.token = token
        self.session.headers["Authorization"] = f"Bearer {token}"
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    raise APIError(
                        error_data.get("detail", str(e)),
                        status_code=e.response.status_code,
                    )
                except ValueError:
                    pass
            raise APIError(str(e))
        except requests.exceptions.ConnectionError:
            raise APIError("Connection failed. Check your internet connection.")
        except requests.exceptions.Timeout:
            raise APIError("Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and get authentication token."""
        return self._request("POST", "/auth/login", data={
            "email": email,
            "password": password,
        })
    
    def get_me(self) -> Dict[str, Any]:
        """Get current user information."""
        return self._request("GET", "/auth/me")
    
    def register_node(self, device_id: str, ip: Optional[str] = None) -> Dict[str, Any]:
        """Register a new node."""
        return self._request("POST", "/node/register", data={
            "deviceId": device_id,
            "ip": ip,
            "name": f"CLI-{platform.node()[:20]}",
        })
    
    def send_heartbeat(
        self,
        node_id: str,
        bandwidth_used: float = 0.0,
        cpu_usage: float = 0.0,
        memory_usage: float = 0.0,
        ip: Optional[str] = None,
        speed_mbps: Optional[float] = None,
        latency_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Send heartbeat to server."""
        return self._request("POST", "/node/heartbeat", data={
            "nodeId": node_id,
            "bandwidthUsed": bandwidth_used,
            "cpuUsage": cpu_usage,
            "memoryUsage": memory_usage,
            "ip": ip,
            "speedMbps": speed_mbps,
            "latencyMs": latency_ms,
        })
    
    def stop_node(self, node_id: str) -> Dict[str, Any]:
        """Stop a node."""
        return self._request("POST", f"/node/stop", params={"nodeId": node_id})
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        return self._request("GET", "/user/stats")
    
    def get_user_nodes(self) -> Dict[str, Any]:
        """Get user's nodes."""
        return self._request("GET", "/user/nodes")


class APIError(Exception):
    """API error exception."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
