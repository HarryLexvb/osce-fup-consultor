# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-17

### Added
- Initial release of OSCE FUP RUC Consultor
- Django 5.0 web application with Clean Architecture
- OSCE API client with httpx for async requests
- Complete provider data aggregation from multiple OSCE endpoints:
  - General data (RUC, business name, SUNAT status, address)
  - Shareholders and partners information
  - Legal representatives
  - Administrative bodies
  - Contract experience
- Excel export functionality with multiple sheets using openpyxl
- Bootstrap 5 responsive UI with professional design
- RUC validation (11 digits numeric)
- Comprehensive error handling and user-friendly messages
- Docker and docker-compose configuration for easy deployment
- Complete test suite with 33 tests (100% passing):
  - Unit tests for forms, client, services, and exporters
  - Integration tests for complete user flows
  - pytest with pytest-django and pytest-httpx
- Code quality tools configuration:
  - black for code formatting
  - isort for import sorting
  - flake8 for linting
  - mypy for type checking
- Complete documentation:
  - Professional README with installation, usage, and architecture
  - API endpoint documentation
  - Troubleshooting guide
- Setup scripts for Windows and Linux
- Makefile for common development tasks
- MIT License

### Technical Details
- Python 3.11+
- Django 5.0.1
- httpx 0.26.0 for async HTTP requests
- openpyxl 3.1.2 for Excel generation
- pytest 7.4.4 with full test coverage
- Type hints throughout the codebase
- Logging configuration for debugging
- Environment variable configuration with python-dotenv

### Security
- User input validation
- CSRF protection enabled
- Non-root user in Docker container
- Environment variables for sensitive configuration
