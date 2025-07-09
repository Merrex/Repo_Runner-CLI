# Repo Runner Architecture

## 🏗️ System Overview

Repo Runner is an agentic microservice backend designed for autonomous repository analysis, setup, and execution. The system operates with an Admin Agent as the CEO, using a manager-agent architecture where managers use decision-making models and agents use generative models.

## 🎯 Core Principles

1. **Admin Agent (CEO)**: Controls the entire system, can create new agents/managers
2. **Manager-Agent Architecture**: Managers use decision-making models, agents use generative models
3. **OrchestratorAgent**: Single POC for user interactions, delegated by Admin Agent
4. **Tier-Based Access**: User capabilities determined by subscription tier
5. **Environment Awareness**: Automatic optimization for different cloud environments
6. **Self-Healing**: Autonomous error detection and resolution
7. **Checkpoint System**: Persistent state management across workflow phases

## 🏛️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   CLI Tool  │  │  Web API    │  │  Colab NB   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 OrchestratorAgent (POC)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  User Authentication & Tier Management            │   │
│  │  Workflow Orchestration & State Management       │   │
│  │  Context Indexer Configuration                   │   │
│  │  Error Handling & Recovery                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Admin Agent (CEO)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  System Control & Agent Creation                  │   │
│  │  Checkpoint Management                            │   │
│  │  Failure Recovery & Intervention                  │   │
│  │  Business Orchestrator Creation                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Manager Network Layer                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Orchestrator│  │   Port      │  │   Model     │      │
│  │  Manager    │  │  Manager    │  │  Manager    │      │
│  │(Decision)   │  │(Decision)   │  │(Decision)   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  Service    │  │  Business   │  │  Custom     │      │
│  │ Orchestrator│  │ Orchestrator│  │  Manager    │      │
│  │(Decision)   │  │(Decision)   │  │(Decision)   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Network Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ EnvDetector │  │ Dependency  │  │   Setup     │      │
│  │   Agent     │  │   Agent     │  │   Agent     │      │
│  │(Generative) │  │(Generative) │  │(Generative) │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Runner    │  │   Health    │  │   Fixer     │      │
│  │   Agent     │  │   Agent     │  │   Agent     │      │
│  │(Generative) │  │(Generative) │  │(Generative) │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Config    │  │   Database  │  │    File     │      │
│  │   Agent     │  │   Agent     │  │   Agent     │      │
│  │(Generative) │  │(Generative) │  │(Generative) │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │Requirements │  │ Detection   │  │ Context     │      │
│  │   Agent     │  │   Agent     │  │  Indexer    │      │
│  │(Generative) │  │(Generative) │  │(Generative) │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   User      │  │   State     │  │   Logging   │      │
│  │ Management  │  │ Management  │  │   System    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Rate      │  │   GPU       │  │   Network   │      │
│  │  Limiting   │  │  Resources  │  │   Access    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 👥 User Management Architecture

### Tier System
```
┌─────────────────────────────────────────────────────────────┐
│                    User Tiers                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │    FREE     │  │  ADVANCED   │  │   PREMIUM   │      │
│  │ Simple Text │  │   FAISS     │  │   Chroma    │      │
│  │ No GPU      │  │ Small GPU   │  │ Large GPU   │      │
│  │ 10 req/hour │  │ 50 req/hour │  │200 req/hour │      │
│  │ No Admin    │  │ No Admin    │  │ No Admin    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   TESTER    │  │    ADMIN    │  │  DEVELOPER  │      │
│  │   FAISS     │  │   Chroma    │  │   Chroma    │      │
│  │ Medium GPU  │  │ Large GPU   │  │ Large GPU   │      │
│  │100 req/hour │  │1000 req/hour│  │10000 req/hr │      │
│  │ No Admin    │  │ No Admin    │  │ ✅ Admin    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### User Management Flow
```
User Registration → Tier Assignment → Authentication → Capability Check → Feature Access
       │                │                │                │                │
       ▼                ▼                ▼                ▼                ▼
   UserManager    TierCapabilities   AuthSystem    FeatureGates    ContextIndexer
```

## 🔄 Workflow Architecture

### Admin Agent (CEO) Workflow
```
1. System Control & Monitoring
   ↓
2. Agent Creation (when needed)
   ↓
3. Checkpoint Management (when new agents created)
   ↓
4. Failure Recovery (when orchestrators fail)
   ↓
5. Business Orchestrator Creation (for custom clients)
   ↓
6. System Intervention (when out of scope)
```

### OrchestratorAgent Workflow
```
1. User Authentication & Tier Validation
   ↓
2. Environment Detection (EnvDetectorAgent)
   ↓
3. Project Analysis (DetectionAgent, RequirementsAgent)
   ↓
4. Dependency Management (DependencyAgent)
   ↓
5. Context Indexer Configuration (based on tier + agent recommendations)
   ↓
6. Setup & Configuration (SetupAgent, ConfigAgent, DatabaseAgent)
   ↓
7. File Processing & Context Indexing (FileAgent, ContextIndexer)
   ↓
8. Service Execution (RunnerAgent)
   ↓
9. Health Monitoring (HealthAgent)
   ↓
10. Error Resolution (FixerAgent)
   ↓
11. Workflow Completion (test_repo run)
   ↓
12. Report to Admin Agent (CEO)
```

### State Management
```
┌─────────────────────────────────────────────────────────────┐
│                    State Management                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   User      │  │   Agent     │  │   Workflow  │      │
│  │   State     │  │   State     │  │   State     │      │
│  │ (users.json)│  │(agent_*.json)│  │(run_state.json)│   │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Admin     │  │   Manager   │  │   Business  │      │
│  │   State     │  │   State     │  │   State     │      │
│  │(admin_*.json)│ │(manager_*.json)│ │(business_*.json)│ │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🧠 Manager-Agent Architecture

### Manager Base Class
```python
class BaseManager:
    def __init__(self):
        self.decision_model = None  # For decision-making tasks
        self.context_awareness = True  # RAG/context access
        self.managed_agents = []  # List of managed agents
    
    def make_decision(self, context):
        """Use decision model for analytical decisions"""
        pass
    
    def coordinate_agents(self, agents, task):
        """Coordinate multiple agents for a task"""
        pass
    
    def checkpoint(self, data):
        """Save manager state"""
        pass
```

### Agent Base Class
```python
class BaseAgent:
    def __init__(self, config=None):
        self.config = config
        self.agent_name = self.__class__.__name__
        self.manager = None  # Reference to managing manager
        self.generative_model = None  # For generative tasks
    
    def run(self, *args, **kwargs):
        """Execute agent workflow"""
        pass
    
    def generate_content(self, prompt):
        """Use generative model for content creation"""
        pass
    
    def checkpoint(self, data):
        """Save agent state"""
        pass
```

### Specialized Managers

#### OrchestratorManager
- **Purpose**: Coordinate workflow and agent execution
- **Model Type**: Decision-making models
- **Output**: Workflow decisions, agent coordination
- **Checkpoint**: `manager_state_OrchestratorManager.json`

#### PortManager
- **Purpose**: Manage port allocation and networking
- **Model Type**: Decision-making models
- **Output**: Port configurations, network decisions
- **Checkpoint**: `manager_state_PortManager.json`

#### ModelManager
- **Purpose**: Manage model selection and configuration
- **Model Type**: Decision-making models
- **Output**: Model configurations, fallback decisions
- **Checkpoint**: `manager_state_ModelManager.json`

### Specialized Agents

#### EnvDetectorAgent
- **Purpose**: Detect cloud environment (Colab, AWS, GCP, local)
- **Model Type**: Generative models
- **Output**: Environment type, capabilities, FAISS recommendations
- **Checkpoint**: `agent_state_EnvDetectorAgent.json`

#### DependencyAgent
- **Purpose**: Manage dependencies with environment-aware versions
- **Model Type**: Generative models
- **Output**: Installed packages, dependency matrix, FAISS recommendations
- **Checkpoint**: `agent_state_DependencyAgent.json`

#### SetupAgent
- **Purpose**: Configure and setup project environment
- **Model Type**: Generative models
- **Output**: Setup status, configuration files, environment variables
- **Checkpoint**: `agent_state_SetupAgent.json`

#### RunnerAgent
- **Purpose**: Execute and run the target application
- **Model Type**: Generative models
- **Output**: Service status, URLs, process information
- **Checkpoint**: `agent_state_RunnerAgent.json`

#### HealthAgent
- **Purpose**: Monitor application health and status
- **Model Type**: Generative models
- **Output**: Health metrics, service status, performance data
- **Checkpoint**: `agent_state_HealthAgent.json`

#### FixerAgent
- **Purpose**: Detect and resolve errors autonomously
- **Model Type**: Generative models
- **Output**: Error fixes, resolution status, recovery actions
- **Checkpoint**: `agent_state_FixerAgent.json`

## 🔍 Context Indexing Architecture

### Tier-Based Access Control
```
┌─────────────────────────────────────────────────────────────┐
│                Context Indexer Access                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   FREE      │  │  ADVANCED   │  │   PREMIUM   │      │
│  │ Simple Text │  │   FAISS     │  │   Chroma    │      │
│  │ (Always)    │  │ (If Rec.)   │  │ (Best Av.)  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   TESTER    │  │    ADMIN    │  │  DEVELOPER  │      │
│  │   FAISS     │  │   Chroma    │  │   Chroma    │      │
│  │ (Always)    │  │ (Best Av.)  │  │ (Best Av.)  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Indexer Selection Logic
```
User Config → Tier Check → Agent Recommendations → Environment Check → Indexer Selection
     │            │              │                    │                │
     ▼            ▼              ▼                    ▼                ▼
  Explicit    Capability    EnvDetectorAgent    DependencyAgent   Final Choice
  Setting     Validation    Recommendations     Recommendations
```

## 🔐 Security Architecture

### Authentication Flow
```
User Input → Password Hashing → User Validation → Tier Assignment → Capability Check
     │              │                │                │                │
     ▼              ▼                ▼                ▼                ▼
  Username    SHA256 Hash    User Lookup    Tier Capabilities    Feature Access
  Password    Storage        Status Check    Rate Limiting       Context Indexer
```

### Authorization Matrix
```
┌─────────────────────────────────────────────────────────────┐
│                    Authorization Matrix                     │
│  Feature          │ Free │ Adv. │ Prem. │ Test │ Admin │ Dev │  │
│  ─────────────────┼──────┼──────┼───────┼──────┼───────┼─────┤  │
│  Simple Search    │  ✅  │  ✅  │  ✅   │  ✅  │  ✅   │  ✅  │  │
│  FAISS Search     │  ❌  │  ✅  │  ✅   │  ✅  │  ✅   │  ✅  │  │
│  Chroma Search    │  ❌  │  ❌  │  ✅   │  ❌  │  ✅   │  ✅  │  │
│  GPU Access       │  ❌  │  ✅  │  ✅   │  ✅  │  ✅   │  ✅  │  │
│  User Management  │  ❌  │  ❌  │  ❌   │  ❌  │  ✅   │  ✅  │  │
│  Admin Functions  │  ❌  │  ❌  │  ❌   │  ❌  │  ✅   │  ✅  │  │
│  Admin Agent      │  ❌  │  ❌  │  ❌   │  ❌  │  ❌   │  ✅  │  │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Monitoring & Observability

### Metrics Collection
```
┌─────────────────────────────────────────────────────────────┐
│                    Metrics Architecture                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Usage     │  │ Performance │  │   Health    │      │
│  │  Metrics    │  │   Metrics   │  │   Metrics   │      │
│  │ - Requests  │  │ - Response  │  │ - Services  │      │
│  │ - Repos     │  │ - Latency   │  │ - Errors    │      │
│  │ - Agents    │  │ - Throughput│  │ - Recovery  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Logging Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Logging Architecture                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Agent     │  │   Manager   │  │   Admin     │      │
│  │   Logs      │  │   Logs      │  │   Logs      │      │
│  │ - Execution │  │ - Decisions │  │ - Control   │      │
│  │ - Results   │  │ - Context   │  │ - Creation  │      │
│  │ - Errors    │  │ - Recovery  │  │ - Recovery  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Deployment Architecture

### Current Deployment
```
┌─────────────────────────────────────────────────────────────┐
│                    Current Deployment                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Local     │  │   Colab     │  │   Docker    │      │
│  │ Development │  │   Testing   │  │   Testing   │      │
│  │ Environment │  │ Environment │  │ Environment │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Future Deployment
```
┌─────────────────────────────────────────────────────────────┐
│                    Future Deployment                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Kubernetes  │  │   AWS EKS   │  │   GCP GKE   │      │
│  │   Cluster   │  │   Cluster   │  │   Cluster   │      │
│  │ - Scalable  │  │ - Managed   │  │ - Managed   │      │
│  │ - HA        │  │ - Auto-scaling│  │ - Auto-scaling│   │
│  │ - Monitoring│  │ - Monitoring│  │ - Monitoring│      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### User Request Flow
```
User Request → CLI/API → OrchestratorAgent → Admin Agent → Manager Network → Agent Network → Response
     │            │            │                │                │                │            │
     ▼            ▼            ▼                ▼                ▼                ▼            ▼
  Authentication Tier Check  Workflow    System Control    Decision Making  Generative    Results
  & Validation  & Limits    Delegation   & Creation       & Coordination    Tasks        & Status
```

### Manager-Agent Communication Flow
```
Manager → Decision Model → Agent → Generative Model → Manager → Checkpoint → Admin Agent
   │           │           │           │              │           │              │
   ▼           ▼           ▼           ▼              ▼           ▼              ▼
Analyze    Make Decision  Execute   Generate Content  Coordinate  Save State    Monitor
Context    & Strategy     Task      & Results        Results     & Recovery    System
```

## 🎯 Key Design Decisions

### 1. Admin Agent as CEO
- **Decision**: Admin Agent controls the entire system
- **Rationale**: Centralized control, agent creation, failure recovery
- **Benefits**: System-wide control, dynamic agent creation, business orchestrator support

### 2. Manager-Agent Architecture
- **Decision**: Managers use decision models, agents use generative models
- **Rationale**: Clear separation of concerns, specialized capabilities
- **Benefits**: Better decision making, specialized task execution, scalability

### 3. Developer Role
- **Decision**: Only Developer role can access Admin Agent
- **Rationale**: Security, controlled access to system control
- **Benefits**: Secure system control, clear access hierarchy

### 4. Business Orchestrators
- **Decision**: Custom orchestrators for business clients
- **Rationale**: Customization, single POC per business
- **Benefits**: Business-specific workflows, isolated environments

### 5. Checkpoint Management
- **Decision**: Admin Agent handles checkpoints only when new agents created
- **Rationale**: Efficient resource usage, focused checkpointing
- **Benefits**: Reduced overhead, targeted state management

## 🔮 Future Architecture Considerations

### Scalability
- **Horizontal Scaling**: Multiple orchestrator instances
- **Load Balancing**: Distribute requests across instances
- **Database**: Move from JSON files to proper database
- **Caching**: Redis for frequently accessed data

### Reliability
- **Circuit Breakers**: Prevent cascade failures
- **Retry Logic**: Automatic retry for transient failures
- **Health Checks**: Comprehensive health monitoring
- **Graceful Degradation**: Continue operation with reduced features

### Security
- **API Gateway**: Centralized security controls
- **Rate Limiting**: Per-user and per-endpoint limits
- **Encryption**: Data encryption at rest and in transit
- **Audit Logging**: Comprehensive audit trails

---

*This architecture document is living and will be updated as the system evolves.* 