# repo_runner

A **modular, agentic AI system** that automatically detects project structure, installs dependencies, configures environments, and runs applications locally or via Docker. Powered by specialized LLM agents for intelligent repository analysis and execution.

---

## 🚀 Installation (Auto-Installation)

### **Option 1: One-Command Installation (Recommended)**

```bash
# Install repo_runner with auto-dependency management
pip install git+https://github.com/Merrex/Repo_Runner-CLI.git

# Auto-install system dependencies
repo_runner install

# Verify installation
repo_runner --help
```

### **Option 2: Development Installation**

```bash
# Clone and install for development
git clone https://github.com/Merrex/Repo_Runner-CLI.git
cd Repo_Runner-CLI/project
pip install -e .

# Auto-install system dependencies
repo_runner install
```

### **Option 3: pipx Installation**

```bash
# Install with pipx (isolated environment)
pipx install git+https://github.com/Merrex/Repo_Runner-CLI.git

# Auto-install system dependencies
repo_runner install
```

> **Note:** The `repo_runner install` command automatically handles:
> - System dependencies (git, node, npm, etc.)
> - Python package dependencies
> - Platform-specific requirements (Linux/macOS/Windows)

---

## 🧠 **Agentic Architecture**

The system consists of specialized AI agents, each optimized for specific tasks:

| Agent | LLM Model | Purpose |
|-------|-----------|---------|
| **DetectionAgent** | Zephyr 1.3B | Intelligent project analysis and structure detection |
| **RequirementsAgent** | Mistral 7B | Generate missing requirements/config files |
| **SetupAgent** | Mistral 7B | Install dependencies and setup environment |
| **DBAgent** | Mistral 7B | Database setup, schema generation, migrations |
| **RunnerAgent** | Mistral 7B | Start applications (Docker, Python, Node.js) |
| **HealthAgent** | Zephyr 1.3B | Health checks and service diagnostics |
| **FixerAgent** | WizardCoder 1B | Error analysis and automatic fixes |

## 🚀 **Features**

🔍 **Intelligent Project Detection**
- LLM-powered analysis of project structure and technologies
- Automatic detection of missing critical files
- Smart identification of frameworks and dependencies

📦 **AI-Generated Requirements**
- Automatically generates `requirements.txt`, `package.json`, `Dockerfile`
- Analyzes existing configs and suggests improvements
- Creates environment files with appropriate defaults

🔧 **Smart Environment Setup**
- LLM-guided dependency installation (pip, npm, yarn, etc.)
- Automatic environment variable generation
- Framework-specific configuration

🗄️ **Database Intelligence**
- Detects database type (SQLite, PostgreSQL, MongoDB, etc.)
- Generates schemas and runs migrations
- Tests database connections automatically

🚀 **Intelligent Application Startup**
- Determines optimal startup method (Docker, Python, Node.js)
- Monitors process health and restarts if needed
- Supports local and cloud deployment modes

🏥 **AI-Powered Health Monitoring**
- Real-time service health checks
- URL response monitoring
- LLM-based issue diagnosis and fixes

🔌 **Extensible Agent System**
- Modular agent architecture for easy extension
- Custom LLM model selection per agent
- Plugin system for new capabilities

## 🎯 **Quick Start**

```bash
repo_runner run /path/to/your/repo --mode local
```

This will:
1. **Detect** project structure using AI
2. **Generate** missing requirements files
3. **Setup** dependencies and environment
4. **Configure** database and run migrations
5. **Start** the application intelligently
6. **Monitor** health and fix issues automatically

## 📋 **Usage Examples**

### **Python Project**

```bash
# Run on a Python project
repo_runner run /path/to/python/project --mode local

# Expected output:
# 🔍 DetectionAgent: Analyzing project structure...
# 📦 RequirementsAgent: Generating requirements.txt...
# 🔧 SetupAgent: Installing dependencies...
# 🗄️ DBAgent: Setting up database...
# 🚀 RunnerAgent: Starting Python application...
# 🏥 HealthAgent: All services healthy!
```

### **Node.js Project**

```bash
# Run on a Node.js project
repo_runner run /path/to/nodejs/project --mode local

# Expected output:
# 🔍 DetectionAgent: Detected React + Express project
# 📦 RequirementsAgent: Generating package.json...
# 🔧 SetupAgent: Running npm install...
# 🗄️ DBAgent: No database detected
# 🚀 RunnerAgent: Starting with npm start...
# 🏥 HealthAgent: Frontend and backend running!
```

### **Docker Project**

```bash
# Run on a Docker project
repo_runner run /path/to/docker/project --mode local

# Expected output:
# 🔍 DetectionAgent: Detected Docker Compose setup
# 📦 RequirementsAgent: Dockerfile already exists
# 🔧 SetupAgent: Building Docker images...
# 🗄️ DBAgent: Database container starting...
# 🚀 RunnerAgent: Starting with docker-compose up...
# 🏥 HealthAgent: All containers healthy!
```

## ⚙️ **Configuration**

### **Agent-Specific Model Configuration**

Create a `.env` file to customize LLM models:

```bash
# Detection and Health (fast, lightweight)
DETECTION_MODEL=HuggingFaceH4/zephyr-1.3b
HEALTH_MODEL=HuggingFaceH4/zephyr-1.3b

# Code Generation (powerful, detailed)
REQUIREMENTS_MODEL=mistralai/Mistral-7B-Instruct-v0.2
SETUP_MODEL=mistralai/Mistral-7B-Instruct-v0.2
DB_MODEL=mistralai/Mistral-7B-Instruct-v0.2
RUNNER_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Code Fixes (specialized)
FIXER_MODEL=WizardLM/WizardCoder-1B-V1.0
```

### **Project Configuration**

Create a `.runnerconfig.yaml` file for project-specific settings:

```yaml
project:
  name: my-project
  type: auto-detect

environment:
  development:
    host: localhost
    port: 8000
    debug: true

database:
  auto_migrate: true
  seed_data: false

docker:
  enabled: true
  detached: false

health_check:
  enabled: true
  timeout: 60
  retry_count: 3
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Missing Dependencies**
   ```bash
   # Auto-install all dependencies
   repo_runner install
   
   # Or manually install if needed
   pip install transformers torch accelerate requests psutil colorama rich jinja2 python-jose[cryptography]
   ```

2. **Permission Issues**
   ```bash
   # Use virtual environment instead of global install
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

3. **LLM Model Loading**
   ```bash
   # Set smaller models for faster loading
   export DETECTION_MODEL="HuggingFaceH4/zephyr-1.3b"
   export FIXER_MODEL="WizardLM/WizardCoder-1B-V1.0"
   ```

### **Debug Mode**

```bash
# Run with verbose logging
repo_runner run /path/to/repo --mode local --verbose
```

## 🏗️ **Architecture**

```
repo_runner/
├── agents/
│   ├── detection_agent.py    # Project analysis
│   ├── requirements_agent.py # Config generation
│   ├── setup_agent.py        # Dependency installation
│   ├── db_agent.py          # Database setup
│   ├── runner_agent.py      # Application startup
│   ├── health_agent.py      # Health monitoring
│   ├── fixer_agent.py       # Error fixing
│   └── orchestrator.py      # Agent coordination
├── llm/
│   └── llm_utils.py         # LLM model management
├── cli.py                   # Command-line interface
└── core.py                  # Core functionality
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run tests: `pytest`
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details.

## 🆘 **Support**

- 📧 Email: info@repo_runner.dev
- 🐛 Issues: GitHub Issues
- 📖 Documentation: GitHub Wiki
- 💬 Discussions: GitHub Discussions