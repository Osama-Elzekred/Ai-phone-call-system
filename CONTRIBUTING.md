# Contributing to AI Hotline Backend

Thank you for considering contributing to AI Hotline Backend! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment following the README instructions
4. Create a new branch for your feature or bug fix

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/ai-hotline-backend.git
cd ai-hotline-backend

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up pre-commit hooks
pip install pre-commit
pre-commit install
```

## Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 88 characters
- Use type hints where appropriate

### Running Code Quality Tools

```bash
# Format code
black app

# Sort imports
isort app

# Lint code
flake8 app

# Type checking
mypy app
```

## Testing

- Write tests for all new features and bug fixes
- Maintain test coverage above 80%
- Use pytest for testing
- Follow the AAA pattern (Arrange, Act, Assert)

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_specific.py
```

## Commit Guidelines

Use conventional commit messages:

- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` formatting changes
- `refactor:` code refactoring
- `test:` adding or updating tests
- `chore:` maintenance tasks

Example:
```
feat: add voice transcription endpoint

- Implement POST /api/v1/calls/transcribe
- Add Munsit-1 API integration
- Include audio file validation
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update the README if you change functionality
5. Submit a pull request with a clear description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs
- Relevant configuration

## Security Vulnerabilities

Do not open public issues for security vulnerabilities. Instead, email security@example.com with details.

## Questions?

Feel free to open a discussion or reach out to the maintainers for any questions about contributing.
