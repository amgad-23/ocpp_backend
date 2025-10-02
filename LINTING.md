# Code Quality & Linting Guide

## Overview
This project uses a comprehensive set of linting tools to maintain high code quality, consistency, and security standards.

## Linting Tools

### 🎨 **Black** - Code Formatter
**Purpose**: Automatic code formatting following PEP 8 standards
**Configuration**: `pyproject.toml`

```bash
# Format all code
black .

# Check formatting without changes
black --check .
```

**Features**:
- 88 character line length
- Consistent string quotes
- Automatic trailing comma handling
- Compatible with flake8 and isort

### 📦 **isort** - Import Sorter
**Purpose**: Organize and sort import statements
**Configuration**: `pyproject.toml`

```bash
# Sort imports
isort .

# Check import sorting
isort --check-only .
```

**Features**:
- Django-aware import grouping
- Black-compatible formatting
- Separates first-party, third-party, and standard library imports

### 📏 **flake8** - Style Checker
**Purpose**: Enforce PEP 8 style guide and detect common errors
**Configuration**: `.flake8`

```bash
# Run style checks
flake8 .

# Generate HTML report
flake8 --format=html --htmldir=flake8-report .
```

**Features**:
- Maximum line length: 88 characters
- Complexity checking (max: 10)
- Excludes migrations and virtual environments
- Compatible with Black formatting

### 🔍 **mypy** - Type Checker
**Purpose**: Static type checking for Python
**Configuration**: `pyproject.toml`

```bash
# Run type checking
mypy .

# Generate detailed report
mypy --html-report mypy-report .
```

**Features**:
- Django plugin support
- Gradual typing (allows untyped code)
- Ignores missing imports for third-party libraries
- Excludes migrations and test files

### 🔒 **bandit** - Security Linter
**Purpose**: Find common security issues in Python code
**Configuration**: `pyproject.toml`

```bash
# Run security checks
bandit -r .

# Generate JSON report
bandit -r . -f json -o bandit-report.json
```

**Features**:
- Scans for security vulnerabilities
- Excludes test files (they may contain intentional security issues)
- Configurable severity levels
- Integration with CI/CD pipelines

### 🔍 **pylint** - Code Analyzer
**Purpose**: Comprehensive code analysis and quality metrics
**Configuration**: `pyproject.toml`

```bash
# Run code analysis
pylint chargers/ ocpp_server/

# Generate detailed report
pylint --output-format=html chargers/ ocpp_server/ > pylint-report.html
```

**Features**:
- Django plugin integration
- Code quality scoring
- Detects code smells and potential bugs
- Configurable message categories

## Pre-commit Hooks

### Setup
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Hooks Configuration
The `.pre-commit-config.yaml` file defines hooks that run automatically:

1. **Built-in hooks**: Trailing whitespace, file endings, YAML validation
2. **Black**: Code formatting
3. **isort**: Import sorting
4. **flake8**: Style checking
5. **mypy**: Type checking
6. **bandit**: Security scanning
7. **Django checks**: Model validation and migration checks

## Makefile Commands

### Quick Commands
```bash
make install     # Install dependencies and setup hooks
make lint        # Run all linting tools
make format      # Format code (black + isort)
make type-check  # Run mypy
make security    # Run bandit
make clean       # Clean cache files
```

### Development Workflow
```bash
make dev-setup   # Complete development environment setup
make dev-check   # Run all checks before committing
make ci          # Simulate CI pipeline
```

## Configuration Files

### `pyproject.toml`
Central configuration for:
- Black formatting options
- isort import sorting
- mypy type checking
- pylint analysis
- bandit security scanning
- pytest test configuration

### `.flake8`
Flake8-specific configuration:
- Line length limits
- Ignored error codes
- Excluded directories
- Per-file ignores

### `.pre-commit-config.yaml`
Pre-commit hooks configuration:
- Hook repositories and versions
- Arguments and additional dependencies
- File patterns and exclusions

## IDE Integration

### VS Code
Add to `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.banditEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm
1. Install Black plugin
2. Configure external tools for flake8, mypy, bandit
3. Enable format on save
4. Configure import optimization

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Lint with flake8
  run: flake8 .

- name: Type check with mypy
  run: mypy .

- name: Security check with bandit
  run: bandit -r .

- name: Format check with black
  run: black --check .
```

### Docker Integration
```dockerfile
# Install linting tools
RUN pip install black flake8 mypy bandit isort

# Run linting in CI
RUN make lint
```

## Troubleshooting

### Common Issues

#### Black and flake8 conflicts
**Solution**: Use compatible configurations in `.flake8`:
```ini
ignore = E203, W503, E501
```

#### Import sorting conflicts
**Solution**: Configure isort with Black profile:
```toml
[tool.isort]
profile = "black"
```

#### MyPy Django issues
**Solution**: Install Django stubs:
```bash
pip install django-stubs
```

#### Pre-commit hook failures
**Solution**: Run hooks manually and fix issues:
```bash
pre-commit run --all-files
```

## Best Practices

1. **Run linting before committing**: Use `make dev-check`
2. **Fix formatting first**: Run `make format` before other checks
3. **Address type hints gradually**: Start with new code, improve existing code over time
4. **Review security warnings**: Don't ignore bandit findings without investigation
5. **Keep configurations updated**: Regularly update tool versions
6. **Use IDE integration**: Configure your editor for real-time feedback

## Metrics and Reports

### Code Quality Metrics
- **Flake8**: Style compliance percentage
- **MyPy**: Type coverage percentage
- **Pylint**: Code quality score (0-10)
- **Bandit**: Security issue count
- **Test Coverage**: Line and branch coverage

### Generating Reports
```bash
# HTML reports
flake8 --format=html --htmldir=reports/flake8 .
mypy --html-report reports/mypy .
bandit -r . -f html -o reports/bandit.html

# Coverage report
pytest --cov=. --cov-report=html --cov-report=term
```

This comprehensive linting setup ensures code quality, security, and maintainability throughout the development lifecycle.
