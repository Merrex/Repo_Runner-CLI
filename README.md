# Repo Runner - Agentic Microservice Backend

A sophisticated, agentic microservice backend system designed for autonomous repository analysis, setup, and execution with tier-based user management and intelligent context indexing.

## 🚀 Features

### Core Architecture
- **Admin Agent (CEO)**: Controls the entire system, can create new agents/managers
- **Manager-Agent Architecture**: Managers use decision-making models, agents use generative models
- **OrchestratorAgent**: Single POC for user interactions, delegated by Admin Agent
- **Tier-Based Access**: User roles with different capabilities (Free, Advanced, Premium, Tester, Admin, Developer)
- **Intelligent Context Indexing**: FAISS/Chroma support with tier-based restrictions
- **Environment Awareness**: Automatic detection and optimization for Colab, AWS, GCP, local
- **Self-Healing**: Autonomous error detection and resolution

### User Tiers & Capabilities

| Tier | Context Indexer | GPU Access | Rate Limit | Max Repos | Admin Agent Access | Support |
|------|----------------|------------|------------|-----------|-------------------|---------|
| **Free** | Simple Text | ❌ | 10/hour | 3 | ❌ | Community |
| **Advanced** | FAISS | Small GPU | 50/hour | 10 | ❌ | Email |
| **Premium** | Chroma | Large GPU | 200/hour | 100 | ❌ | Priority |
| **Tester** | FAISS | Medium GPU | 100/hour | 50 | ❌ | Internal |
| **Admin** | Chroma | Large GPU | 1000/hour | 1000 | ❌ | Admin |
| **Developer** | Chroma | Large GPU | 10000/hour | 10000 | ✅ | Developer |

### Key Features
- **Admin Agent (CEO)**: Only accessible by Developer role, controls everything
- **Manager-Agent Pattern**: Managers use RAG/context awareness, agents use generative models
- **Business Orchestrators**: Custom orchestrators for business clients as single POC
- **Agent Creation**: Admin Agent can create new agents and managers dynamically
- **Checkpoint Management**: Admin Agent handles checkpoints only when new agents need creation
- **Failure Recovery**: Admin Agent intervenes when orchestrators fail to report success

## 🏗️ Architecture

```
User/3rd Party → OrchestratorAgent (Single POC) → Admin Agent (CEO)
                                    ↓                    ↓
                            Manager Network        System Control
                                    ↓                    ↓
                            Agent Network         Agent Creation
                                    ↓                    ↓
                            Context Indexer       Failure Recovery
                                    ↓                    ↓
                            Environment Detection  Business Orchestrators
```

### **Admin Agent (CEO) - Indirect Orchestration:**
- **Admin Agent**: Controls and orchestrates the OrchestratorAgent (POC)
- **All Users**: Indirectly benefit from Admin Agent's capabilities through OrchestratorAgent
- **Direct Access**: Only Developer can directly access Admin Agent
- **Indirect Access**: All users get Admin Agent's capabilities through OrchestratorAgent

### **Workflow:**
```
User Request → OrchestratorAgent (POC) → Admin Agent (CEO) → OrchestratorAgent (Enhanced) → Response
     │              │                        │                        │
     ▼              ▼                        ▼                        ▼
User Input    Single POC              System Control         Best System Capabilities
             for Users              & Orchestration         Delivered to User
```

## 🧠 Manager-Agent Architecture

### Managers (Decision-Making)
- **Use RAG/Context Awareness**: Access to knowledge bases and context
- **Decision Models**: Specialized in analytical and decision-making tasks
- **Workflow Control**: Coordinate and orchestrate agent activities
- **Checkpoint Management**: Save and restore system state
- **Examples**: OrchestratorManager, PortManager, ModelManager

### Agents (Generative Tasks)
- **Use Generative Models**: Create content, code, configurations
- **Specialized Tasks**: Each agent has specific domain expertise
- **Managed by Managers**: Receive instructions and report results
- **Examples**: DetectionAgent, SetupAgent, RunnerAgent, FixerAgent

### Admin Agent (CEO)
- **System Control**: Controls all orchestrators and managers
- **Agent Creation**: Creates new agents and managers when needed
- **Checkpoint Management**: Handles checkpoints only when new agents need creation
- **Failure Recovery**: Intervenes when orchestrators fail to report success
- **Developer Access**: Only accessible by users with 'developer' role
- **Business Orchestrator Creation**: Creates custom orchestrators for business clients
- **Indirect Orchestration**: All users benefit from Admin Agent capabilities through OrchestratorAgent

## 🛠️ Installation

```bash
# Clone the repository
git clone <repository-url>
cd repo_runner

# Install dependencies
pip install -r requirements.txt

# Register as developer (first time only)
python -m repo_runner.cli --register --username developer --password your_password --tier developer

# Login
python -m repo_runner.cli --login --username developer --password your_password
```

## 📖 Usage

### Basic Usage
```bash
# Run with default settings (free tier)
python -m repo_runner.cli --repo_path /path/to/repo

# Run with authentication
python -m repo_runner.cli --login --username your_user --password your_pass --repo_path /path/to/repo
```

### Developer Commands (Admin Agent Access)
```bash
# Access Admin Agent (Developer only)
python -m repo_runner.cli --login --username developer --password dev_pass --admin_agent create_agent --agent_type custom_detection

# Create business orchestrator
python -m repo_runner.cli --login --username developer --password dev_pass --admin_agent create_business_orchestrator --business_name acme_corp

# Intervene in orchestrator failure
python -m repo_runner.cli --login --username developer --password dev_pass --admin_agent intervene --orchestrator_id main_orchestrator
```

### Admin Commands (User Management)
```bash
# List all users
python -m repo_runner.cli --login --username admin --password admin_pass --list_users

# Upgrade user
python -m repo_runner.cli --login --username admin --password admin_pass --upgrade_user user1 --new_tier advanced

# Block user
python -m repo_runner.cli --login --username admin --password admin_pass --block_user user1
```

## 🔧 Configuration

### Environment Variables
```bash
# Model configuration
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key

# GPU configuration (for Premium/Admin/Developer)
export CUDA_VISIBLE_DEVICES=0
```

### Configuration File
```json
{
  "repo_path": "/path/to/repo",
  "environment": "detect",
  "model_tier": "balanced",
  "faiss": {
    "use_faiss": null,
    "sentence_transformer_model": "all-MiniLM-L6-v2"
  },
  "skip_agents": [],
  "log_level": "INFO"
}
```

## 🧪 Testing

### Run Complete System Test
```bash
python test_complete_system.py
```

### Test Individual Components
```bash
# Test user management
python test_tier_system.py

# Test FAISS configuration
python test_faiss_config.py
```

## 📊 Workflow Phases

1. **Environment Detection**: Detect Colab, AWS, GCP, local
2. **Dependency Analysis**: Environment-aware package management
3. **Setup & Configuration**: Database, config, file processing
4. **Context Indexing**: Tier-based FAISS/Chroma/simple indexing
5. **Service Orchestration**: Start and monitor services
6. **Health Monitoring**: Continuous health checks
7. **Error Resolution**: Autonomous error fixing

## 🔒 Security & Permissions

### User Management
- **Developer**: Can access Admin Agent (CEO), create agents/managers, system control
- **Admin**: Can manage users, but cannot access Admin Agent
- **Tester**: Same privileges as admin except user management
- **Premium/Advanced**: Can use advanced features based on tier
- **Free**: Limited to basic features and simple text search

### Context Indexer Access
- **Free/Tester**: Always use simple text search
- **Advanced**: Can use FAISS if recommended by agents
- **Premium/Admin/Developer**: Can use Chroma (best available)
- **Agent Recommendations**: Only applied for Advanced/Premium users

### Admin Agent Access
- **Developer**: Full access to Admin Agent (CEO)
- **All Other Tiers**: No access to Admin Agent
- **Business Clients**: Get custom orchestrators as single POC

## 📈 Monitoring & Logging

### Checkpoint Files
- `run_state.json`: Overall workflow state
- `agent_state_*.json`: Individual agent states
- `admin_agent_state.json`: Admin Agent state
- `users.json`: User management data

### Usage Tracking
- Repository creation count
- Agent usage statistics
- Rate limit monitoring
- GPU resource utilization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Free Tier**: Community support
- **Advanced Tier**: Email support
- **Premium Tier**: Priority support
- **Tester/Admin**: Internal support
- **Developer**: Direct access to Admin Agent

## 🔄 Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development plans and current status. 