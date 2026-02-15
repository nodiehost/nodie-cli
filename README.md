# Nodie CLI

<p align="center">
  <img src="https://nodie.host/logo.png" alt="Nodie Logo" width="120">
</p>

<p align="center">
  <strong>Turn your terminal into a network node. Earn rewards for sharing bandwidth.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/nodie-cli/"><img src="https://img.shields.io/pypi/v/nodie-cli.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/nodie-cli/"><img src="https://img.shields.io/pypi/pyversions/nodie-cli.svg" alt="Python versions"></a>
  <a href="https://github.com/nicofirst1/nodie-cli/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

---

## 🚀 Features

- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Headless Operation**: Run as a background service or daemon
- **Auto-Reconnect**: Automatically reconnects if connection is lost
- **Real-Time Stats**: View your earnings and node statistics
- **Low Resource Usage**: Minimal CPU and memory footprint

## 📦 Installation

### Using pip (Recommended)

```bash
pip install nodie-cli
```

### Using pipx (Isolated Environment)

```bash
pipx install nodie-cli
```

### From Source

```bash
git clone https://github.com/nicofirst1/nodie-cli.git
cd nodie-cli
pip install -e .
```

## 🔧 Quick Start

### 1. Login to your account

```bash
nodie login
```

You'll be prompted for your email and password. Your credentials are stored securely.

### 2. Start the node

```bash
nodie start
```

### 3. Check your stats

```bash
nodie stats
```

### 4. Stop the node

```bash
nodie stop
```

## 📖 Commands

| Command | Description |
|---------|-------------|
| `nodie login` | Login to your Nodie account |
| `nodie logout` | Logout and clear credentials |
| `nodie start` | Start the node and begin earning |
| `nodie stop` | Stop the running node |
| `nodie status` | Check if node is running |
| `nodie stats` | View your earnings and statistics |
| `nodie config` | View or update configuration |
| `nodie speedtest` | Run a network speed test |
| `nodie version` | Show version information |

## ⚙️ Configuration

Configuration file location:
- **Linux/macOS**: `~/.config/nodie/config.json`
- **Windows**: `%APPDATA%\nodie\config.json`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODIE_API_URL` | API endpoint URL | `https://nodie.host/api` |
| `NODIE_CONFIG_DIR` | Config directory path | Platform default |
| `NODIE_LOG_LEVEL` | Logging level | `INFO` |

## 🖥️ Running as a Service

### Linux (systemd)

```bash
# Create service file
sudo nodie install-service

# Enable and start
sudo systemctl enable nodie
sudo systemctl start nodie
```

### macOS (launchd)

```bash
nodie install-service --user
```

### Windows (Task Scheduler)

```bash
nodie install-service
```

## 🔒 Security

- Credentials are stored encrypted using your system's keyring
- All communication uses HTTPS
- No personal data or browsing history is collected
- Only bandwidth metrics are transmitted

## 📊 Earnings

Points are calculated based on:
- **Connection Quality**: Good (≥30 Mbps) = 0.5 pts/min, Bad (<30 Mbps) = 0.1 pts/min
- **IP Type**: Residential IPs earn full rate, Datacenter IPs earn 30%
- **Uptime**: The longer you run, the more you earn

## 🐛 Troubleshooting

### Node won't connect

1. Check your internet connection
2. Verify your credentials: `nodie login`
3. Check API status: `nodie status --verbose`

### Low points earnings

1. Run speed test: `nodie speedtest`
2. Ensure you have a residential IP (not VPN/datacenter)
3. Keep the node running 24/7 for maximum earnings

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

```bash
# Clone the repository
git clone https://github.com/nicofirst1/nodie-cli.git
cd nodie-cli

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- **Website**: https://nodie.host
- **Documentation**: https://nodie.host/docs
- **Support**: https://nodie.host/support
- **Browser Extension**: [Chrome](https://chromewebstore.google.com/detail/nodie-decentralized-node/mdppdjfemekfodneapklbadphhegpdca) | [Firefox](https://addons.mozilla.org/firefox/addon/nodie/)

---

<p align="center">
  Made with ❤️ by the Nodie Team
</p>
