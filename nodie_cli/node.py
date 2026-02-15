"""
Node management and operation.
"""

import hashlib
import os
import platform
import signal
import sys
import threading
import time
import uuid
from typing import Callable, Optional

import psutil
import requests

from nodie_cli.client import NodieClient, APIError
from nodie_cli.config import get_config_value, get_pid_file


class NodieNode:
    """Manages node operations including heartbeats and statistics."""
    
    def __init__(self, client: NodieClient):
        self.client = client
        self.device_id = self._get_or_create_device_id()
        self.node_id: Optional[str] = None
        self.is_running = False
        self.stats = {
            "uptime_seconds": 0,
            "bandwidth_used": 0.0,
            "points_earned": 0.0,
            "heartbeats_sent": 0,
        }
        self.node_info = {}
        self._stop_event = threading.Event()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._on_stats_update: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
    
    def _get_or_create_device_id(self) -> str:
        """Get or create a unique device ID."""
        from nodie_cli.config import get_config_dir
        
        device_file = get_config_dir() / "device_id"
        
        if device_file.exists():
            return device_file.read_text().strip()
        
        # Generate device ID based on machine info
        machine_info = f"{platform.node()}-{platform.machine()}-{uuid.getnode()}"
        device_id = f"cli_{hashlib.sha256(machine_info.encode()).hexdigest()[:24]}"
        
        device_file.write_text(device_id)
        return device_id
    
    def _get_public_ip(self) -> Optional[str]:
        """Get public IP address."""
        services = [
            "https://api.ipify.org?format=json",
            "https://api.my-ip.io/v2/ip.json",
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=10)
                if response.ok:
                    data = response.json()
                    return data.get("ip") or data.get("ip_address")
            except Exception:
                continue
        return None
    
    def measure_speed(self) -> tuple[float, float]:
        """Measure network speed and latency."""
        speed_mbps = 0.0
        latency_ms = 100.0
        
        try:
            # Measure latency
            ping_times = []
            for _ in range(3):
                start = time.time()
                requests.head("https://www.google.com/favicon.ico", timeout=5)
                ping_times.append((time.time() - start) * 1000)
            latency_ms = min(ping_times)
            
            # Measure download speed
            start = time.time()
            response = requests.get(
                "https://httpbin.org/bytes/102400",
                timeout=30,
            )
            elapsed = time.time() - start
            size_mb = len(response.content) / (1024 * 1024)
            speed_mbps = (size_mb / elapsed) * 8
            
            # Cap at reasonable values
            speed_mbps = min(max(speed_mbps, 0.1), 1000)
            
        except Exception:
            speed_mbps = 5.0
            latency_ms = 200.0
        
        return speed_mbps, latency_ms
    
    def _get_system_stats(self) -> tuple[float, float]:
        """Get CPU and memory usage."""
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            return cpu_usage, memory_usage
        except Exception:
            return 0.0, 0.0
    
    def _heartbeat_loop(self) -> None:
        """Main heartbeat loop."""
        interval = get_config_value("heartbeat_interval", 30)
        speedtest_interval = get_config_value("speedtest_interval", 300)
        last_speedtest = 0
        
        while not self._stop_event.is_set():
            try:
                # Get current IP
                ip = self._get_public_ip()
                
                # Measure speed periodically
                now = time.time()
                if now - last_speedtest >= speedtest_interval:
                    speed_mbps, latency_ms = self.measure_speed()
                    last_speedtest = now
                else:
                    speed_mbps = self.node_info.get("speedMbps", 0)
                    latency_ms = self.node_info.get("latencyMs", 100)
                
                # Get system stats
                cpu_usage, memory_usage = self._get_system_stats()
                
                # Send heartbeat
                result = self.client.send_heartbeat(
                    node_id=self.node_id,
                    bandwidth_used=0.1,
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    ip=ip,
                    speed_mbps=speed_mbps,
                    latency_ms=latency_ms,
                )
                
                # Update stats
                self.stats["uptime_seconds"] += interval
                self.stats["bandwidth_used"] += 0.1
                self.stats["points_earned"] += result.get("pointsEarned", 0)
                self.stats["heartbeats_sent"] += 1
                
                # Update node info
                self.node_info.update({
                    "networkScore": result.get("networkScore", 30),
                    "ipType": result.get("ipType", "unknown"),
                    "connectionQuality": result.get("connectionQuality", "unknown"),
                    "speedMbps": speed_mbps,
                    "latencyMs": latency_ms,
                    "ip": ip,
                })
                
                if self._on_stats_update:
                    self._on_stats_update(self.stats, self.node_info)
                
            except APIError as e:
                if self._on_error:
                    self._on_error(f"Heartbeat failed: {e.message}")
            except Exception as e:
                if self._on_error:
                    self._on_error(f"Error: {e}")
            
            # Wait for next interval or stop signal
            self._stop_event.wait(interval)
    
    def start(
        self,
        on_stats_update: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ) -> dict:
        """Start the node."""
        if self.is_running:
            raise RuntimeError("Node is already running")
        
        self._on_stats_update = on_stats_update
        self._on_error = on_error
        
        # Get public IP
        ip = self._get_public_ip()
        
        # Run initial speed test
        speed_mbps, latency_ms = self.measure_speed()
        
        # Register node
        result = self.client.register_node(self.device_id, ip)
        self.node_id = result["id"]
        
        self.node_info = {
            "nodeId": self.node_id,
            "deviceId": self.device_id,
            "networkScore": result.get("networkScore", 30),
            "ipType": result.get("ipType", "unknown"),
            "country": result.get("country"),
            "countryCode": result.get("countryCode"),
            "speedMbps": speed_mbps,
            "latencyMs": latency_ms,
            "ip": ip,
        }
        
        # Save PID
        pid_file = get_pid_file()
        pid_file.write_text(str(os.getpid()))
        
        # Start heartbeat thread
        self._stop_event.clear()
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True,
        )
        self._heartbeat_thread.start()
        
        self.is_running = True
        return self.node_info
    
    def stop(self) -> None:
        """Stop the node."""
        if not self.is_running:
            return
        
        # Signal stop
        self._stop_event.set()
        
        # Wait for thread to finish
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)
        
        # Notify server
        if self.node_id:
            try:
                self.client.stop_node(self.node_id)
            except Exception:
                pass
        
        # Remove PID file
        pid_file = get_pid_file()
        if pid_file.exists():
            pid_file.unlink()
        
        self.is_running = False
    
    @staticmethod
    def is_node_running() -> bool:
        """Check if a node is already running."""
        pid_file = get_pid_file()
        if not pid_file.exists():
            return False
        
        try:
            pid = int(pid_file.read_text().strip())
            return psutil.pid_exists(pid)
        except (ValueError, IOError):
            return False
    
    @staticmethod
    def get_running_pid() -> Optional[int]:
        """Get the PID of the running node."""
        pid_file = get_pid_file()
        if not pid_file.exists():
            return None
        
        try:
            pid = int(pid_file.read_text().strip())
            if psutil.pid_exists(pid):
                return pid
        except (ValueError, IOError):
            pass
        return None
