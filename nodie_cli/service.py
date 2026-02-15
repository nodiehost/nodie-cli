"""
Service installation for background operation.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def get_python_path() -> str:
    """Get the path to the Python interpreter."""
    return sys.executable


def get_nodie_path() -> str:
    """Get the path to the nodie command."""
    # Try to find nodie in the same directory as Python
    python_dir = Path(sys.executable).parent
    nodie_path = python_dir / "nodie"
    if nodie_path.exists():
        return str(nodie_path)
    
    # Try Windows .exe
    nodie_exe = python_dir / "nodie.exe"
    if nodie_exe.exists():
        return str(nodie_exe)
    
    # Fall back to just "nodie"
    return "nodie"


def install_systemd_service() -> bool:
    """Install systemd service for Linux."""
    service_content = f"""[Unit]
Description=Nodie Node - Decentralized Network Node
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
ExecStart={get_nodie_path()} start --foreground
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_path = Path("/etc/systemd/system/nodie.service")
    
    try:
        service_path.write_text(service_content)
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        print(f"✓ Service installed at {service_path}")
        print("\nTo start the service:")
        print("  sudo systemctl enable nodie")
        print("  sudo systemctl start nodie")
        return True
    except PermissionError:
        print("Error: Permission denied. Run with sudo.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def install_launchd_service(user_level: bool = True) -> bool:
    """Install launchd service for macOS."""
    label = "host.nodie.node"
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{get_nodie_path()}</string>
        <string>start</string>
        <string>--foreground</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/nodie.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/nodie.stderr.log</string>
</dict>
</plist>
"""
    
    if user_level:
        plist_dir = Path.home() / "Library" / "LaunchAgents"
    else:
        plist_dir = Path("/Library/LaunchDaemons")
    
    plist_dir.mkdir(parents=True, exist_ok=True)
    plist_path = plist_dir / f"{label}.plist"
    
    try:
        plist_path.write_text(plist_content)
        print(f"✓ Service installed at {plist_path}")
        print("\nTo start the service:")
        print(f"  launchctl load {plist_path}")
        return True
    except PermissionError:
        print("Error: Permission denied. Run with sudo for system-level service.")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def install_windows_task() -> bool:
    """Install Windows Task Scheduler task."""
    nodie_path = get_nodie_path()
    
    try:
        # Create a scheduled task that runs at login
        cmd = [
            "schtasks", "/create",
            "/tn", "NodieNode",
            "/tr", f'"{nodie_path}" start --foreground',
            "/sc", "onlogon",
            "/rl", "limited",
            "/f",
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Task created successfully")
            print("\nTo start the task now:")
            print("  schtasks /run /tn NodieNode")
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def install_service(user_level: bool = True) -> bool:
    """Install service based on the current platform."""
    system = platform.system()
    
    if system == "Linux":
        return install_systemd_service()
    elif system == "Darwin":
        return install_launchd_service(user_level)
    elif system == "Windows":
        return install_windows_task()
    else:
        print(f"Unsupported platform: {system}")
        return False


def uninstall_service() -> bool:
    """Uninstall the service."""
    system = platform.system()
    
    try:
        if system == "Linux":
            subprocess.run(["systemctl", "stop", "nodie"], check=False)
            subprocess.run(["systemctl", "disable", "nodie"], check=False)
            service_path = Path("/etc/systemd/system/nodie.service")
            if service_path.exists():
                service_path.unlink()
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            print("✓ Service uninstalled")
            return True
        
        elif system == "Darwin":
            label = "host.nodie.node"
            for plist_dir in [
                Path.home() / "Library" / "LaunchAgents",
                Path("/Library/LaunchDaemons"),
            ]:
                plist_path = plist_dir / f"{label}.plist"
                if plist_path.exists():
                    subprocess.run(["launchctl", "unload", str(plist_path)], check=False)
                    plist_path.unlink()
            print("✓ Service uninstalled")
            return True
        
        elif system == "Windows":
            subprocess.run(["schtasks", "/delete", "/tn", "NodieNode", "/f"], check=True)
            print("✓ Task deleted")
            return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return False
