# Contributing to NotebookLM MCP Server

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and considerate in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/notebooklm-mcp.git
   cd notebooklm-mcp
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/notebooklm-mcp.git
   ```

## Development Setup

### Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (for containerization testing)
- Kubernetes/Helm (for deployment testing)

### Installation

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Install Playwright browsers:
   ```bash
   uv run playwright install chromium
   ```

3. Set up authentication:
   ```bash
   uv run python scripts/setup_auth.py
   ```

4. Create a `.env` file (optional):
   ```bash
   cp .env.example .env
   ```

## Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   or
   ```bash
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes following the [Style Guidelines](#style-guidelines)

3. Test your changes locally:
   ```bash
   # Run the server
   uv run notebooklm-mcp

   # Test with MCP Inspector
   npx @modelcontextprotocol/inspector uv --directory . run notebooklm-mcp
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add new feature" # or "fix: resolve bug"
   ```

   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Adding or updating tests
   - `chore:` - Maintenance tasks

## Testing

### Local Testing
```bash
# Test listing notebooks
uv run python test_final.py

# Test with headless browser
NOTEBOOKLM_HEADLESS=true uv run notebooklm-mcp

# Test with visible browser
NOTEBOOKLM_HEADLESS=false uv run notebooklm-mcp
```

### Docker Testing
```bash
# Build image
docker build -t notebooklm-mcp:test .

# Run container
docker-compose up
```

### Helm Testing
```bash
# Lint chart
helm lint helm/notebooklm-mcp

# Dry run
helm install test-release helm/notebooklm-mcp --dry-run --debug

# Template output
helm template test-release helm/notebooklm-mcp
```

## Submitting Changes

1. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request:
   - Go to the repository on GitHub
   - Click "Pull requests" > "New pull request"
   - Select your branch
   - Fill out the PR template
   - Submit the PR

3. Address review feedback:
   - Make requested changes
   - Push updates to your branch
   - Respond to comments

## Style Guidelines

### Python Code Style
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for functions and classes

Example:
```python
async def list_notebooks() -> List[Dict[str, str]]:
    """
    List all available NotebookLM notebooks.

    Returns:
        List of notebooks with id, title, and url
    """
    pass
```

### Documentation
- Use clear, concise language
- Include code examples where helpful
- Update README.md if adding new features
- Add inline comments for complex logic

### Commits
- Write clear commit messages
- Reference issues in commits (e.g., `fixes #123`)
- Keep commits focused and atomic

### Docker
- Optimize for image size
- Use multi-stage builds
- Follow security best practices
- Document all ENV variables

### Helm Charts
- Follow Helm best practices
- Use meaningful default values
- Document all values in values.yaml
- Test with different configurations

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- [ ] Add unit tests and integration tests
- [ ] Improve error handling and logging
- [ ] Add support for more NotebookLM features
- [ ] Improve authentication flow
- [ ] Add monitoring and observability

### Medium Priority
- [ ] Performance optimizations
- [ ] Better documentation
- [ ] Example use cases and tutorials
- [ ] CI/CD improvements
- [ ] Security enhancements

### Low Priority
- [ ] Additional deployment options
- [ ] UI for configuration
- [ ] Additional language support
- [ ] Plugin system

## Questions?

If you have questions:
- Check existing issues
- Open a new issue with the "question" label
- Join discussions in existing PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
