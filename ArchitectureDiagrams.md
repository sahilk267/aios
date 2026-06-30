# AIOS - Architecture Diagrams

## 1. System Overview

### 1.1 High-Level Architecture

```mermaid
graph TB
    subgraph "AIOS Desktop Application"
        direction TB
        FE["Frontend<br/>Tauri + React + TypeScript"]
        API["API Gateway<br/>FastAPI + Pydantic"]
        
        subgraph "Core Services"
            AE["Agent Engine"]
            WE["Workflow Engine"]
            MS["Memory Service"]
            KB["Knowledge Base"]
            PM["Plugin Manager"]
            PR["Provider Router"]
            SS["Security Service"]
            OS["Observability"]
        end
        
        subgraph "Data Layer"]
            DB[("SQLite<br/>Primary DB")]
            VD[("Qdrant<br/>Vector Store")]
            GD[("NetworkX<br/>Graph Store")]
            FS["File System<br/>Logs/Artifacts"]
        end
    end
    
    subgraph "External Systems"
        OP["Ollama<br/>Local Models"]
        OR["OpenRouter<br/>Free API"]
        LT["LiteLLM<br/>Proxy"]
        VS["IDEs<br/>VS Code, Cursor"]
        GT["Git<br/>Version Control"]
        DK["Docker<br/>Containers"]
    end
    
    FE -->|"HTTP/WebSocket"| API
    API --> AE
    API --> WE
    API --> MS
    API --> KB
    API --> PM
    API --> SS
    
    AE --> MS
    AE --> KB
    AE --> PR
    WE --> AE
    WE --> MS
    MS --> DB
    MS --> VD
    MS --> GD
    KB --> VD
    KB --> DB
    PM --> SS
    PR --> OP
    PR --> OR
    PR --> LT
    SS --> DB
    OS --> FS
    AE -->|"publish events"| API
    WE -->|"publish events"| API
    
    FE -->|"IDE Extensions"| VS
    AE -->|"Git operations"| GT
    AE -->|"Container ops"| DK
```

### 1.2 Layered Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI["Dashboard"]
        AG["Agent Monitor"]
        WF["Workflow Designer"]
        MEM["Memory Explorer"]
        KB["Knowledge Browser"]
        CFG["Configuration"]
    end
    
    subgraph "API Layer"
        AGW["API Gateway<br/>Auth + Routing + Rate Limiting"]
        WS["WebSocket Server<br/>Real-time Events"]
    end
    
    subgraph "Service Layer"
        AES["Agent Engine"]
        WFS["Workflow Engine"]
        MMS["Memory Service"]
        KBS["Knowledge Base"]
        PMS["Plugin Manager"]
        PRS["Provider Router"]
        SEC["Security Service"]
        OBS["Observability"]
    end
    
    subgraph "Data Access Layer"]
        DAL["Repository Pattern"]
        VSL["Vector Store Adapter"]
        GSL["Graph Store Adapter"]
    end
    
    subgraph "Storage Layer"]
        SQLITE[("SQLite")]
        QDRANT[("Qdrant")]
        NETWORKX[("NetworkX")]
        FILES["File System"]
    end
    
    UI --> AGW
    AG --> AGW
    WF --> AGW
    MEM --> AGW
    KB --> AGW
    CFG --> AGW
    
    AGW --> AES
    AGW --> WFS
    AGW --> MMS
    AGW --> KBS
    AGW --> PMS
    AGW --> SEC
    
    WS --> OBS
    WS --> AES
    WS --> WFS
    
    AES --> MMS
    AES --> KBS
    AES --> PRS
    WFS --> AES
    
    AES --> DAL
    MMS --> DAL
    MMS --> VSL
    MMS --> GSL
    KBS --> DAL
    KBS --> VSL
    
    DAL --> SQLITE
    VSL --> QDRANT
    GSL --> NETWORKX
    OBS --> FILES
```

## 2. Agent Architecture

### 2.1 Agent Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Registered: Agent created
    Registered --> Idle: Initialized
    Idle --> Running: Task assigned
    Running --> Waiting: Awaiting approval / dependency
    Waiting --> Running: Approval granted / dependency met
    Running --> Completed: Task finished
    Running --> Failed: Error occurred
    Failed --> Idle: Retry
    Failed --> Terminated: Max retries exceeded
    Completed --> Idle: Ready for next task
    Terminated --> [*]
    
    state Running {
        [*] --> Preparing
        Preparing --> Executing: Resources ready
        Executing --> Validating: Output generated
        Validating --> [*]: Output valid
    }
    
    state Waiting {
        [*] --> AwaitingApproval
        [*] --> AwaitingDependency
        AwaitingApproval --> Running: Approved
        AwaitingApproval --> Terminated: Rejected
        Aependency --> Running: Dependency resolved
    }
```

### 2.2 Agent Communication

```mermaid
sequenceDiagram
    participant U as User
    participant AE as Agent Engine
    participant P as Planner Agent
    participant A as Architect Agent
    participant B as Backend Agent
    participant R as Reviewer Agent
    participant W as Workflow Engine
    
    U->>AE: Create workflow "Implement Feature"
    AE->>W: Start workflow
    W->>P: Task: Plan feature
    P->>AE: Request memory context
    AE-->>P: Return relevant memories
    P-->>W: Return plan
    W->>A: Task: Design architecture
    A-->>P: Query plan details
    A-->>W: Return design
    W->>B: Task: Implement code
    B-->>A: Query design
    B-->>W: Return code
    W->>R: Task: Review code
    R-->>B: Query implementation
    R-->>W: Return review
    W-->>AE: Workflow complete
    AE-->>U: Notify completion
```

### 2.3 Multi-Agent Collaboration Patterns

```mermaid
graph LR
    subgraph "Collaboration Patterns"
        direction TB
        
        subgraph "Sequential"
            S1["Agent A"] --> S2["Agent B"] --> S3["Agent C"]
        end
        
        subgraph "Parallel"
            P1["Coordinator"] --> P2["Agent A"]
            P1 --> P3["Agent B"]
            P1 --> P4["Agent C"]
            P2 --> P5["Merge"]
            P3 --> P5
            P4 --> P5
        end
        
        subgraph "Hierarchical"
            H1["Lead Agent"] --> H2["Sub-Agent A"]
            H1 --> H3["Sub-Agent B"]
            H2 --> H4["Sub-Sub-Agent"]
            H3 --> H4
        end
        
        subgraph "Review Cycle"
            R1["Worker"] --> R2["Reviewer"]
            R2 -->|"Approve"| R3["Complete"]
            R2 -->|"Reject"| R1
        end
    end
```

## 3. Workflow Architecture

### 3.1 Workflow DAG

```mermaid
graph TD
    START([Start]) --> PLAN["Plan Feature"]
    PLAN --> DESIGN["Design Architecture"]
    DESIGN --> IMPLEMENT["Implement Code"]
    DESIGN --> TEST_PLAN["Plan Tests"]
    IMPLEMENT --> CODE_REVIEW["Code Review"]
    TEST_PLAN --> CODE_REVIEW
    CODE_REVIEW -->|"Changes Needed"| IMPLEMENT
    CODE_REVIEW -->|"Approved"| TEST["Run Tests"]
    TEST -->|"Failures"| FIX["Fix Issues"]
    FIX --> TEST
    TEST -->|"Pass"| DOCS["Generate Documentation"]
    DOCS --> SECURITY["Security Scan"]
    SECURITY -->|"Vulnerabilities"| FIX
    SECURITY -->|"Clean"| DEPLOY["Deploy"]
    DEPLOY --> END([End])
    
    style START fill:#2d2d2d,color:#fff
    style END fill:#2d2d2d,color:#fff
```

### 3.2 Workflow Engine Architecture

```mermaid
graph TB
    subgraph "Workflow Engine"
        direction TB
        WD["Workflow Definition<br/>(DAG Parser)"]
        DR["Dependency Resolver"]
        TS["Task Scheduler"]
        PE["Parallel Executor"]
        AG["Approval Gate"]
        WH["Workflow History"]
        
        WD --> DR
        DR --> TS
        TS --> PE
        PE --> AG
        AG -->|"Approved"| TS
        AG -->|"Rejected"| TS
        PE --> WH
        TS --> WH
    end
    
    subgraph "Task States"
        direction LR
        T1["Pending"] --> T2["Scheduled"]
        T2 --> T3["Running"]
        T3 --> T4["Completed"]
        T3 --> T5["Failed"]
        T5 --> T1
    end
```

## 4. Memory Architecture

### 4.1 Memory Type Hierarchy

```mermaid
graph TB
    subgraph "Memory Systems"
        direction TB
        
        STM["Short-Term Memory<br/>Session context<br/>In-memory + TTL"]
        LTM["Long-Term Memory<br/>Persistent context<br/>SQLite"]
        
        subgraph "Specialized Memory"
            VM["Vector Memory<br/>Semantic search<br/>Qdrant"]
            GM["Graph Memory<br/>Relationships<br/>NetworkX"]
            DM["Decision Memory<br/>Choices + rationale<br/>SQLite"]
            PM["Project Memory<br/>Project context<br/>SQLite"]
            CM["Conversation Memory<br/>Chat history<br/>SQLite"]
            AM["Architecture Memory<br/>Design decisions<br/>SQLite"]
            LM["Learning Memory<br/>Patterns + improvements<br/>SQLite"]
        end
        
        STM -->|"Consolidation"| LTM
        STM -->|"Indexing"| VM
        STM -->|"Relationships"| GM
        LTM -->|"Decisions"| DM
        LTM -->|"Projects"| PM
        LTM -->|"Conversations"| CM
        LTM -->|"Architecture"| AM
        LTM -->|"Learnings"| LM
    end
```

### 4.2 Memory Flow

```mermaid
sequenceDiagram
    participant AG as Agent
    participant MS as Memory Service
    participant ST as Short-Term Store
    participant LT as Long-Term Store
    participant VS as Vector Store
    participant GS as Graph Store
    
    AG->>MS: Store observation
    MS->>ST: Write to short-term
    MS->>VS: Generate embedding
    MS->>GS: Extract relationships
    
    Note over MS: Consolidation cycle
    MS->>ST: Read recent entries
    ST-->>MS: Return entries
    MS->>LT: Promote to long-term
    MS->>VS: Update vector index
    MS->>GS: Update graph
    
    AG->>MS: Query memory
    MS->>VS: Semantic search
    VS-->>MS: Relevant vectors
    MS->>GS: Graph traversal
    GS-->>MS: Related nodes
    MS-->>AG: Return consolidated results
```

## 5. Provider Architecture

### 5.1 Provider Abstraction

```mermaid
classDiagram
    class BaseProvider {
        <<abstract>>
        +chat_completion(messages, **kwargs) Response
        +stream_completion(messages, **kwargs) AsyncIterator~Response~
        +list_models() List~Model~
        +get_capabilities(model) ModelCapabilities
        +count_tokens(text, model) int
    }
    
    class OllamaProvider {
        +base_url: str
        +chat_completion(messages, **kwargs) Response
        +list_models() List~Model~
    }
    
    class OpenRouterProvider {
        +api_key: str
        +chat_completion(messages, **kwargs) Response
        +list_models() List~Model~
    }
    
    class LiteLLMProvider {
        +base_url: str
        +api_key: str
        +chat_completion(messages, **kwargs) Response
    }
    
    class vLLMProvider {
        +base_url: str
        +chat_completion(messages, **kwargs) Response
    }
    
    BaseProvider <|-- OllamaProvider
    BaseProvider <|-- OpenRouterProvider
    BaseProvider <|-- LiteLLMProvider
    BaseProvider <|-- vLLMProvider
```

### 5.2 Request Routing Flow

```mermaid
flowchart TD
    A[Task Request] --> B{Capability Required?}
    B -->|Yes| C[Filter by Capability]
    B -->|No| D[All Providers]
    C --> E{Provider Available?}
    D --> E
    E -->|Yes| F[Check Rate Limits]
    E -->|No| G[Fallback Chain]
    F --> H{Within Limits?}
    H -->|Yes| I[Route to Provider]
    H -->|No| G
    I --> J[Execute Request]
    J --> K{Success?}
    K -->|Yes| L[Return Response]
    K -->|No| M{Retryable?}
    M -->|Yes| G
    M -->|No| N[Return Error]
```

## 6. Security Architecture

### 6.1 Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant AG as API Gateway
    participant AU as Auth Service
    participant RBAC as RBAC Engine
    participant SEC as Security Service
    participant DB as Database
    
    U->>AG: Login request
    AG->>AU: Authenticate
    AU->>DB: Verify credentials
    DB-->>AU: User record
    AU->>AU: Generate JWT
    AU-->>AG: JWT token
    AG-->>U: Token + session
    
    U->>AG: API request + JWT
    AG->>AU: Validate token
    AU-->>AG: Token valid
    AG->>RBAC: Check permission
    RBAC->>DB: Get role permissions
    DB-->>RBAC: Permissions
    RBAC-->>AG: Access granted/denied
    AG->>SEC: Log access
    SEC->>DB: Write audit log
    AG-->>U: Response
```

### 6.2 RBAC Model

```mermaid
graph TD
    subgraph "RBAC Model"
        direction TB
        
        U["Users"] -->|"assigned to"| R["Roles"]
        R -->|"has"| P["Permissions"]
        P -->|"on"| RES["Resources"]
        
        subgraph "Roles"
            ADMIN["Admin"]
            PO["Project Owner"]
            DEV["Developer"]
            VIEWER["Viewer"]
            AGENT["Agent"]
        end
        
        subgraph "Permissions"
            READ["Read"]
            WRITE["Write"]
            EXECUTE["Execute"]
            DELETE["Delete"]
            ADMIN_PERM["Admin"]
        end
        
        subgraph "Resources"
            PROJ["Projects"]
            AGT["Agents"]
            WF["Workflows"]
            MEM["Memory"]
            KB["Knowledge"]
            PLG["Plugins"]
            SYS["System"]
        end
    end
```

## 7. Plugin Architecture

### 7.1 Plugin Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Discovered: Plugin found
    Discovered --> Validated: Signature check
    Validated --> Loaded: Module loaded
    Loaded --> Sandboxed: Isolated execution
    Sandboxed --> Registered: API registered
    Registered --> Active: Plugin running
    Active --> Disabled: Admin disables
    Disabled --> Active: Admin enables
    Active --> Unloaded: App shutdown
    Unloaded --> [*]
    
    state Sandboxed {
        [*] --> ProcessIsolation
        ProcessIsolation --> ResourceLimits
        ResourceLimits --> PermissionCheck
        PermissionCheck --> [*]
    }
```

### 7.2 Plugin System Architecture

```mermaid
graph TB
    subgraph "Plugin System"
        direction TB
        PL["Plugin Loader"]
        PV["Plugin Validator"]
        PS["Plugin Sandbox"]
        PR["Plugin Registry"]
        PA["Plugin API"]
        
        PL --> PV
        PV -->|"Valid"| PS
        PS --> PR
        PR --> PA
    end
    
    subgraph "Plugin Types"
        direction LR
        AGT["Agent Plugins"]
        TOL["Tool Plugins"]
        PVD["Provider Plugins"]
        WFL["Workflow Plugins"]
        MEM["Memory Plugins"]
    end
    
    PA --> AGT
    PA --> TOL
    PA --> PVD
    PA --> WFL
    PA --> MEM
```

## 8. Deployment Architecture

### 8.1 Local-First Desktop

```mermaid
graph TB
    subgraph "Developer Machine"
        direction TB
        
        subgraph "AIOS Desktop"
            Tauri["Tauri Runtime<br/>(Rust Backend)"]
            React["React Frontend<br/>(TypeScript)"]
            Python["Python Backend<br/>(FastAPI)"]
            
            Tauri --> React
            Tauri <--> Python
        end
        
        subgraph "Embedded Storage"
            SQLite[("SQLite")]
            Qdrant[("Qdrant")]
            NetworkX[("NetworkX")]
        end
        
        subgraph "Local Models"
            Ollama["Ollama Server"]
            vLLM["vLLM Server"]
        end
        
        Python --> SQLite
        Python --> Qdrant
        Python --> NetworkX
        Python --> Ollama
        Python --> vLLM
    end
    
    subgraph "Optional External"
        Git["GitHub/Gitea"]
        OR["OpenRouter"]
    end
    
    Python -.->|"Git ops"| Git
    Python -.->|"API calls"| OR
```

### 8.2 Data Flow

```mermaid
flowchart LR
    subgraph "User Interaction"
        UI["UI Events"]
    end
    
    subgraph "Frontend"
        Hooks["React Hooks"]
        Stores["State Stores"]
        API["API Client"]
    end
    
    subgraph "Backend"
        Gateway["API Gateway"]
        Services["Business Logic"]
        Storage["Data Access"]
    end
    
    subgraph "External"
        Providers["AI Models"]
        Tools["Dev Tools"]
    end
    
    UI --> Hooks
    Hooks --> Stores
    Stores --> API
    API -->|"HTTP/WebSocket"| Gateway
    Gateway --> Services
    Services --> Storage
    Services -->|"API calls"| Providers
    Services -->|"executes"| Tools
    Providers -->|"responses"| Services
    Services -->|"events"| Gateway
    Gateway -->|"WebSocket"| API
    API -->|"updates"| Stores
    Stores -->|"re-render"| UI
```

## 9. Observability Architecture

### 9.1 Three Pillars

```mermaid
graph TB
    subgraph "Observability Stack"
        direction TB
        
        subgraph "Logging"
            LS["Structured Logs<br/>(structlog)"]
            LF["Log Files"]
            LQ["Log Query"]
            LS --> LF
            LF --> LQ
        end
        
        subgraph "Metrics"
            MC["Metrics Collection<br/>(Prometheus)"]
            MD["Metrics Dashboard<br/>(Grafana)"]
            MA["Alerting"]
            MC --> MD
            MD --> MA
        end
        
        subgraph "Tracing"
            TC["Trace Collection<br/>(OpenTelemetry)"]
            TV["Trace Visualization"]
            TP["Performance Analysis"]
            TC --> TV
            TV --> TP
        end
    end
    
    subgraph "Application"
        APP["AIOS Services"]
        APP -->|"emit"| LS
        APP -->|"expose"| MC
        APP -->|"instrument"| TC
    end
```

## 10. Self-Improvement Architecture

### 10.1 Improvement Cycle

```mermaid
flowchart TD
    A[Monitor Performance] --> B[Identify Patterns]
    B --> C[Generate Hypotheses]
    C --> D[Design Experiments]
    D --> E[Run A/B Tests]
    E --> F{Analyze Results}
    F -->|Significant Improvement| G[Propose Change]
    F -->|No Improvement| H[Discard Hypothesis]
    G --> I{Human Approval?}
    I -->|Approved| J[Apply Improvement]
    I -->|Rejected| H
    J --> K[Monitor Results]
    K --> A
    H --> A
```

### 10.2 Self-Improvement Data Flow

```mermaid
sequenceDiagram
    participant AE as Agent Engine
    participant SM as Self-Improvement Monitor
    participant PA as Pattern Analyzer
    participant PE as Proposal Engine
    participant HA as Human Approval
    participant CM as Change Manager
    participant PM as Prompt/Config Store
    
    AE->>SM: Log execution metrics
    SM->>PA: Aggregate patterns
    PA-->>SM: Pattern report
    SM->>PE: Generate proposals
    PE-->>SM: Improvement proposals
    SM->>HA: Present for approval
    alt Approved
        HA->>CM: Approve change
        CM->>PM: Apply change
        CM->>AE: Update configuration
    else Rejected
        HA->>SM: Reject proposal
    end
```
