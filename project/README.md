# repo_runner

A comprehensive Python CLI tool that automatically detects project structure, installs dependencies, configures environments, and runs applications locally or via Docker. Perfect for automation pipelines and developer workflows.

## Features

🔍 **Automatic Project Detection**
- Detects backend (Python/Django/Flask/FastAPI), frontend (React/Vue/Angular), Docker, and database configurations
- Identifies package managers (pip, poetry, npm, yarn, pnpm)
- Recognizes CI/CD configurations

📦 **Smart Dependency Installation**
- Supports Python (pip, poetry, pipenv) and Node.js (npm, yarn, pnpm) package managers
- Handles Docker-based setups automatically
- Parallel installation when possible

🔧 **Environment Configuration**
- Automatic .env file setup from examples
- Environment variable validation
- Framework-specific configuration

🗄️ **Database Bootstrapping**
- Supports SQLite, PostgreSQL, Prisma, Alembic, Django migrations
- Automatic database creation and seeding
- Connection validation

🚀 **Application Startup**
- Runs applications directly or via Docker
- Supports multiple services simultaneously
- Graceful shutdown handling

🏥 **Health Checks & Monitoring**
- Service health validation
- Response time monitoring
- Port availability checking

📚 **Documentation Management**
- Auto-updates README.md with setup instructions
- Generates setup guides
- Creates .env.example files

🔌 **Extensible Architecture**
- Custom hooks system (pre_install, post_run, etc.)
- Plugin support via .runnerconfig.yaml
- Modular design for easy extension

## Installation

```bash
pip install repo_runner
```

## Quick Start

### Automatic Workflow (Recommended)

```bash
# Run complete workflow: detect, setup, and run
repo_runner full

# Or run individual steps
repo_runner detect    # Detect project structure
repo_runner setup     # Install dependencies and configure
repo_runner run       # Run the application
```

### Individual Commands

```bash
# Detect project structure
repo_runner detect

# Install dependencies only
repo_runner setup --skip-env --skip-db

# Run with custom port
repo_runner run --port 8080

# Force Docker execution
repo_runner run --docker

# Check application health
repo_runner health

# Update documentation
repo_runner docs
```

## Configuration

Create a `.runnerconfig.yaml` file to customize behavior:

```yaml
project:
  name: my-project
  type: auto-detect

environment:
  development:
    host: localhost
    port: 3000
    debug: true

database:
  auto_migrate: true
  seed_data: true

docker:
  enabled: true
  detached: false

hooks:
  pre_install:
    - echo "Preparing installation..."
  post_run:
    - echo "Application started!"

health_check:
  enabled: true
  timeout: 60
```

## Supported Project Types

### Backend Frameworks
- **Django**: Full support with migrations and admin setup
- **Flask**: Automatic detection and environment setup
- **FastAPI**: Modern async API framework support
- **Generic Python**: Any Python project with requirements.txt

### Frontend Frameworks
- **React**: Create React App and Vite support
- **Vue.js**: Vue CLI and Vite support
- **Angular**: Angular CLI support
- **Next.js**: Full-stack React framework
- **Nuxt.js**: Vue-based framework

### Databases
- **SQLite**: Automatic database creation
- **PostgreSQL**: Connection validation and migrations
- **Prisma**: Schema generation and migrations
- **Alembic**: SQLAlchemy migrations
- **Django ORM**: Built-in migration support

### Package Managers
- **Python**: pip, poetry, pipenv
- **Node.js**: npm, yarn, pnpm
- **Docker**: Dockerfile and docker-compose

## Hook System

Extend repo_runner with custom hooks:

### Create hooks.py

```python
def pre_install(structure=None, **kwargs):
    """Called before dependency installation."""
    print("🔧 Preparing for installation...")
    
def post_run(structure=None, services=None, **kwargs):
    """Called after application starts."""
    print("🎉 Application is running!")
    
def pre_health(services=None, **kwargs):
    """Called before health check."""
    print("🏥 Checking application health...")
```

### Available Hook Points

- `pre_detect` / `post_detect`: Project structure detection
- `pre_install` / `post_install`: Dependency installation
- `pre_env` / `post_env`: Environment setup
- `pre_db` / `post_db`: Database configuration
- `pre_run` / `post_run`: Application startup
- `pre_health` / `post_health`: Health checks
- `pre_docs` / `post_docs`: Documentation updates

## Examples

### Django Project

```bash
# Detect Django project
repo_runner detect
# Output: Django project with PostgreSQL database

# Setup with migrations
repo_runner setup
# Installs dependencies, runs migrations, creates superuser

# Run development server
repo_runner run
# Starts Django on http://localhost:8000
```

### React + Node.js API

```bash
# Detect full-stack project
repo_runner detect
# Output: Frontend (React) + Backend (Node.js) + Database (PostgreSQL)

# Install all dependencies
repo_runner setup

# Run both frontend and backend
repo_runner run
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

### Docker Project

```bash
# Force Docker execution
repo_runner run --docker

# Or with docker-compose
repo_runner full  # Automatically detects and uses docker-compose
```

## CLI Reference

### Commands

- `detect`: Analyze project structure and technologies
- `setup`: Install dependencies and configure environment
- `run`: Start the application
- `full`: Complete workflow (detect + setup + run)
- `health`: Check application health
- `docs`: Update project documentation

### Global Options

- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging
- `--dry-run`: Show what would be done without executing

### Run Options

- `--port, -p`: Override default port
- `--host, -h`: Override default host
- `--docker`: Force Docker execution
- `--no-health-check`: Skip health validation

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/repo_runner/repo_runner.git
cd repo_runner

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 repo_runner/
black repo_runner/
```

### Project Structure

```
repo_runner/
├── __init__.py          # Package initialization
├── cli.py               # CLI interface
├── core.py              # Main RepoRunner class
├── detectors.py         # Project structure detection
├── installers.py        # Dependency installation
├── environment.py       # Environment configuration
├── database.py          # Database management
├── runner.py            # Application execution
├── health.py            # Health checking
├── documentation.py     # Documentation updates
├── hooks.py             # Hook system
├── config.py            # Configuration management
└── logger.py            # Logging setup
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📧 Email: info@repo_runner.dev
- 🐛 Issues: GitHub Issues
- 📖 Documentation: GitHub Wiki
- 💬 Discussions: GitHub Discussions