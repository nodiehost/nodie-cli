# Contributing to Nodie CLI

Thank you for your interest in contributing to Nodie CLI! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all experience levels.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip or pipx

### Setting Up Development Environment

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nodie-cli.git
   cd nodie-cli
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=nodie_cli --cov-report=html
```

### Code Style

We use the following tools for code quality:

- **ruff** - Linting
- **black** - Code formatting
- **mypy** - Type checking

Run all checks:
```bash
ruff check .
black --check .
mypy nodie_cli
```

Auto-fix issues:
```bash
ruff check --fix .
black .
```

## Making Changes

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates

### Commit Messages

Follow conventional commits:

- `feat: add new speedtest command`
- `fix: handle connection timeout`
- `docs: update installation instructions`
- `test: add tests for node module`
- `chore: update dependencies`

### Pull Requests

1. Create a new branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Update documentation if needed
5. Run all tests and linting
6. Push to your fork
7. Open a pull request

### PR Checklist

- [ ] Tests pass
- [ ] Code is formatted with black
- [ ] No ruff warnings
- [ ] Documentation updated (if applicable)
- [ ] Changelog updated (for user-facing changes)

## Project Structure

```
nodie-cli/
├── nodie_cli/
│   ├── __init__.py     # Package info
│   ├── cli.py          # CLI commands
│   ├── client.py       # API client
│   ├── config.py       # Configuration
│   ├── auth.py         # Authentication
│   ├── node.py         # Node management
│   └── service.py      # Service installation
├── tests/
│   ├── test_client.py
│   ├── test_config.py
│   └── ...
├── pyproject.toml      # Project config
├── README.md
└── CONTRIBUTING.md
```

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Full error message/traceback
- Steps to reproduce

## Questions?

Feel free to open an issue for questions or join our community channels:

- Discord: [Nodie Community](https://discord.gg/nodie)
- Forum: [Nodie Discussions](https://github.com/nicofirst1/nodie-cli/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
