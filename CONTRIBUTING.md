# Contributing to OSCE FUP RUC Consultor

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/HarryLexvb/osce-fup-ruc-consultor.git
cd osce-fup-ruc-consultor
```

2. **Set up development environment**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

3. **Run migrations**

```bash
python manage.py migrate
```

## Development Workflow

### Before Making Changes

1. **Create a new branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Ensure all tests pass**

```bash
pytest
```

### Making Changes

1. **Write tests first (TDD approach)**
   - Create test files in `fup_consult/tests/`
   - Write failing tests for your new feature
   - Implement the feature until tests pass

2. **Follow code style guidelines**
   - Use type hints for all functions
   - Follow PEP 8 conventions
   - Write docstrings for public functions
   - Keep functions small and focused

3. **Format your code**

```bash
black .
isort .
```

4. **Run linting**

```bash
flake8
mypy fup_consult/
```

### Testing Requirements

**All tests must pass at 100% before submitting a PR.**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fup_consult --cov-report=html

# Run specific test categories
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
```

### Commit Guidelines

- Use clear, descriptive commit messages
- Follow conventional commits format:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `test:` for test additions/modifications
  - `refactor:` for code refactoring
  - `chore:` for maintenance tasks

Example:
```
feat: add support for filtering contracts by date range

- Added date range filters to experience section
- Updated Excel export to include filtered data
- Added tests for date filtering logic
```

### Pull Request Process

1. **Ensure all checks pass**
   - All tests passing (33/33 or more)
   - Code formatted with black and isort
   - No flake8 errors
   - Type checking passes

2. **Update documentation**
   - Update README.md if adding new features
   - Add entries to CHANGELOG.md
   - Update docstrings and comments

3. **Submit PR**
   - Provide clear description of changes
   - Reference any related issues
   - Include screenshots for UI changes

## Code Style

### Python Style Guide

- **Line length**: Maximum 100 characters
- **Imports**: Grouped and sorted by isort
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for all public functions

Example:
```python
def get_provider_data(ruc: str, include_experience: bool = True) -> ProviderData:
    """
    Get complete provider data for given RUC.

    Args:
        ruc: Provider's RUC number (11 digits)
        include_experience: Whether to include contract experience

    Returns:
        Complete provider data with all sections

    Raises:
        OSCEAPIException: If API request fails
    """
    # Implementation
```

### Django Best Practices

- Keep views thin, logic in services
- Use class-based views when appropriate
- Validate data in forms
- Handle errors gracefully with user-friendly messages

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test complete user flows
- **Use fixtures**: Define reusable test data in `conftest.py`
- **Mock external APIs**: Use `pytest-httpx` for API mocking

### Test Example

```python
@pytest.mark.unit
def test_validate_ruc_format(self) -> None:
    """Test RUC validation accepts valid format."""
    form = RUCSearchForm(data={"ruc": "20508238143"})
    assert form.is_valid()
```

## Documentation

- Keep README.md up to date
- Document new features in CHANGELOG.md
- Add inline comments for complex logic
- Update API documentation if endpoints change

## Questions or Issues?

- Open an issue for bugs or feature requests
- Use discussions for questions
- Tag issues appropriately (bug, enhancement, question)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
