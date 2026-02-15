"""
Nodie CLI - Main command line interface.
"""

import os
import signal
import sys
import time
from typing import Optional

import click
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from nodie_cli import __version__
from nodie_cli.auth import clear_credentials, get_credentials, get_token, save_credentials
from nodie_cli.client import APIError, NodieClient
from nodie_cli.config import get_config_dir, load_config, save_config
from nodie_cli.node import NodieNode

console = Console()


def print_banner():
    """Print the Nodie banner."""
    banner = """
[cyan]╔═╗╔═╗╔═╗═══════════════════════════════════╗
║ ║║ ║║ ║  [bold white]NODIE CLI[/bold white]                        ║
║ ╚╝ ║║ ║  [dim]Turn your terminal into a node[/dim]      ║
║    ║╚═╝  [dim]Earn rewards for sharing bandwidth[/dim] ║
╚════╝═════════════════════════════════════════╝[/cyan]
"""
    console.print(banner)


@click.group()
@click.version_option(version=__version__, prog_name="nodie")
def main():
    """Nodie CLI - Turn your terminal into a network node."""
    pass


@main.command()
def login():
    """Login to your Nodie account."""
    print_banner()
    
    # Check if already logged in
    creds = get_credentials()
    if creds:
        console.print(f"[yellow]Already logged in as {creds.get('email')}[/yellow]")
        if not click.confirm("Do you want to login with a different account?"):
            return
    
    console.print("\n[bold]Login to Nodie[/bold]\n")
    
    email = click.prompt("Email")
    password = click.prompt("Password", hide_input=True)
    
    client = NodieClient()
    
    with console.status("[bold cyan]Logging in...[/bold cyan]"):
        try:
            result = client.login(email, password)
            token = result.get("token")
            
            # Get user info
            client.set_token(token)
            user = client.get_me()
            
            # Save credentials
            save_credentials(email, token, user.get("id"))
            
            console.print(f"\n[green]✓ Logged in successfully![/green]")
            console.print(f"  Welcome, [bold]{user.get('username')}[/bold]!")
            console.print(f"  Total Points: [cyan]{user.get('totalPoints', 0):.2f}[/cyan]")
            
        except APIError as e:
            console.print(f"\n[red]✗ Login failed: {e.message}[/red]")
            sys.exit(1)


@main.command()
def logout():
    """Logout and clear saved credentials."""
    clear_credentials()
    console.print("[green]✓ Logged out successfully[/green]")


@main.command()
@click.option("--foreground", "-f", is_flag=True, help="Run in foreground (don't daemonize)")
def start(foreground: bool):
    """Start the node and begin earning."""
    print_banner()
    
    # Check credentials
    token = get_token()
    if not token:
        console.print("[red]✗ Not logged in. Run 'nodie login' first.[/red]")
        sys.exit(1)
    
    # Check if already running
    if NodieNode.is_node_running():
        pid = NodieNode.get_running_pid()
        console.print(f"[yellow]Node is already running (PID: {pid})[/yellow]")
        console.print("Run 'nodie stop' to stop it first.")
        sys.exit(1)
    
    client = NodieClient(token)
    node = NodieNode(client)
    
    # Set up signal handlers
    def handle_signal(signum, frame):
        console.print("\n[yellow]Stopping node...[/yellow]")
        node.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Start node
    console.print("[bold cyan]Starting node...[/bold cyan]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Measuring network speed...", total=None)
        
        try:
            node_info = node.start()
            progress.remove_task(task)
        except APIError as e:
            progress.remove_task(task)
            console.print(f"[red]✗ Failed to start: {e.message}[/red]")
            sys.exit(1)
    
    # Display node info
    console.print("[green]✓ Node started successfully![/green]\n")
    
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Key", style="dim")
    info_table.add_column("Value")
    info_table.add_row("Node ID", node_info.get("nodeId", "")[:12] + "...")
    info_table.add_row("Device ID", node_info.get("deviceId", "")[:12] + "...")
    info_table.add_row("IP Address", node_info.get("ip", "Unknown"))
    info_table.add_row("Country", node_info.get("country", "Unknown"))
    info_table.add_row("IP Type", node_info.get("ipType", "Unknown"))
    info_table.add_row("Network Score", f"{node_info.get('networkScore', 0)}%")
    info_table.add_row("Speed", f"{node_info.get('speedMbps', 0):.1f} Mbps")
    
    console.print(Panel(info_table, title="Node Information", border_style="cyan"))
    
    if foreground:
        console.print("\n[dim]Running in foreground. Press Ctrl+C to stop.[/dim]\n")
        
        # Live stats display
        def on_stats_update(stats, info):
            pass  # Stats will be displayed in the live table
        
        def on_error(error):
            console.print(f"[red]{error}[/red]")
        
        node._on_stats_update = on_stats_update
        node._on_error = on_error
        
        try:
            while node.is_running:
                # Create stats table
                stats_table = Table(show_header=False, box=None)
                stats_table.add_column("Key", style="dim")
                stats_table.add_column("Value", style="cyan")
                
                uptime = node.stats["uptime_seconds"]
                hours, remainder = divmod(uptime, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                stats_table.add_row("Uptime", f"{int(hours)}h {int(minutes)}m {int(seconds)}s")
                stats_table.add_row("Points Earned", f"{node.stats['points_earned']:.4f}")
                stats_table.add_row("Heartbeats", str(node.stats["heartbeats_sent"]))
                stats_table.add_row("Connection", node.node_info.get("connectionQuality", "unknown").upper())
                stats_table.add_row("Speed", f"{node.node_info.get('speedMbps', 0):.1f} Mbps")
                
                console.clear()
                print_banner()
                console.print(Panel(stats_table, title="[green]● Node Running[/green]", border_style="green"))
                console.print("\n[dim]Press Ctrl+C to stop[/dim]")
                
                time.sleep(5)
        except KeyboardInterrupt:
            pass
        
        node.stop()
        console.print("\n[green]✓ Node stopped[/green]")
    else:
        console.print("\n[green]Node is running in background.[/green]")
        console.print("Use 'nodie status' to check status")
        console.print("Use 'nodie stop' to stop the node")


@main.command()
def stop():
    """Stop the running node."""
    if not NodieNode.is_node_running():
        console.print("[yellow]No node is currently running.[/yellow]")
        return
    
    pid = NodieNode.get_running_pid()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            console.print(f"[green]✓ Sent stop signal to node (PID: {pid})[/green]")
        except ProcessLookupError:
            console.print("[yellow]Node process not found.[/yellow]")
        except PermissionError:
            console.print("[red]Permission denied. Try with sudo.[/red]")


@main.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def status(verbose: bool):
    """Check if node is running."""
    print_banner()
    
    is_running = NodieNode.is_node_running()
    pid = NodieNode.get_running_pid()
    
    if is_running:
        console.print(f"[green]● Node is running[/green] (PID: {pid})")
    else:
        console.print("[red]● Node is not running[/red]")
    
    if verbose:
        token = get_token()
        if token:
            client = NodieClient(token)
            try:
                user = client.get_me()
                console.print(f"\n[bold]Account:[/bold] {user.get('email')}")
                console.print(f"[bold]Total Points:[/bold] {user.get('totalPoints', 0):.2f}")
            except APIError:
                pass


@main.command()
def stats():
    """View your earnings and statistics."""
    print_banner()
    
    token = get_token()
    if not token:
        console.print("[red]✗ Not logged in. Run 'nodie login' first.[/red]")
        sys.exit(1)
    
    client = NodieClient(token)
    
    with console.status("[bold cyan]Fetching stats...[/bold cyan]"):
        try:
            user = client.get_me()
            nodes = client.get_user_nodes()
        except APIError as e:
            console.print(f"[red]✗ Failed to fetch stats: {e.message}[/red]")
            sys.exit(1)
    
    # User info
    console.print(f"\n[bold]Account: {user.get('username')}[/bold]")
    console.print(f"Email: {user.get('email')}\n")
    
    # Points
    points_table = Table(title="Points Summary", show_header=True)
    points_table.add_column("Metric", style="dim")
    points_table.add_column("Value", style="cyan", justify="right")
    points_table.add_row("Total Points", f"{user.get('totalPoints', 0):.2f}")
    points_table.add_row("Referral Code", user.get("referralCode", "N/A"))
    
    console.print(points_table)
    
    # Nodes
    if nodes.get("nodes"):
        nodes_table = Table(title="\nYour Nodes", show_header=True)
        nodes_table.add_column("Name")
        nodes_table.add_column("Status")
        nodes_table.add_column("IP Type")
        nodes_table.add_column("Score")
        nodes_table.add_column("Country")
        
        for n in nodes["nodes"]:
            status_color = "green" if n.get("status") == "online" else "red"
            nodes_table.add_row(
                n.get("name", "Unknown"),
                f"[{status_color}]{n.get('status', 'unknown')}[/{status_color}]",
                n.get("ipType", "unknown"),
                f"{n.get('networkScore', 0)}%",
                n.get("country", "Unknown"),
            )
        
        console.print(nodes_table)
    else:
        console.print("\n[dim]No nodes registered yet.[/dim]")


@main.command()
def speedtest():
    """Run a network speed test."""
    print_banner()
    
    console.print("[bold]Running speed test...[/bold]\n")
    
    node = NodieNode(NodieClient())
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing connection...", total=None)
        speed_mbps, latency_ms = node.measure_speed()
        progress.remove_task(task)
    
    # Results
    results_table = Table(show_header=False, box=None)
    results_table.add_column("Metric", style="dim")
    results_table.add_column("Value", style="cyan")
    
    results_table.add_row("Download Speed", f"{speed_mbps:.2f} Mbps")
    results_table.add_row("Latency", f"{latency_ms:.0f} ms")
    
    quality = "GOOD" if speed_mbps >= 30 else "BAD"
    quality_color = "green" if speed_mbps >= 30 else "red"
    results_table.add_row("Connection Quality", f"[{quality_color}]{quality}[/{quality_color}]")
    
    # Points rate
    if speed_mbps >= 30:
        rate = "0.5 pts/min (residential) or 0.15 pts/min (datacenter)"
    else:
        rate = "0.1 pts/min (residential) or 0.03 pts/min (datacenter)"
    results_table.add_row("Estimated Rate", rate)
    
    console.print(Panel(results_table, title="Speed Test Results", border_style="cyan"))


@main.command()
@click.option("--set", "set_value", nargs=2, help="Set a config value (key value)")
def config(set_value):
    """View or update configuration."""
    print_banner()
    
    if set_value:
        key, value = set_value
        cfg = load_config()
        
        # Try to convert to appropriate type
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.isdigit():
            value = int(value)
        
        cfg[key] = value
        save_config(cfg)
        console.print(f"[green]✓ Set {key} = {value}[/green]")
    else:
        cfg = load_config()
        
        config_table = Table(title="Configuration", show_header=True)
        config_table.add_column("Key", style="dim")
        config_table.add_column("Value")
        
        for key, value in cfg.items():
            config_table.add_row(key, str(value))
        
        console.print(config_table)
        console.print(f"\n[dim]Config directory: {get_config_dir()}[/dim]")


@main.command("install-service")
@click.option("--user", "user_level", is_flag=True, help="Install for current user only (macOS)")
def install_service(user_level: bool):
    """Install Nodie as a system service."""
    print_banner()
    
    from nodie_cli.service import install_service as do_install
    
    console.print("[bold]Installing Nodie service...[/bold]\n")
    success = do_install(user_level)
    
    if not success:
        sys.exit(1)


@main.command("uninstall-service")
def uninstall_service():
    """Uninstall the system service."""
    from nodie_cli.service import uninstall_service as do_uninstall
    
    console.print("[bold]Uninstalling Nodie service...[/bold]\n")
    success = do_uninstall()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
