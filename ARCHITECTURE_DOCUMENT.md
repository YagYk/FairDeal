# FairDeal Architecture Document

## Document Information

**Project:** FairDeal - AI-Powered Contract Analysis Platform  
**Version:** 1.0  
**Date:** January 2025  
**Team:** Final Year Project  
**Architecture Type:** Monolithic Architecture with Modular Design

---

## Table of Contents

1. [Architecture Selection](#1-architecture-selection)
2. [Architecture Overview](#2-architecture-overview)
3. [Use Case Diagrams](#3-use-case-diagrams)
4. [Class Diagrams](#4-class-diagrams)
5. [Data Flow Diagrams (DFD)](#5-data-flow-diagrams-dfd)
6. [Component Diagrams](#6-component-diagrams)
7. [Sequence Diagrams](#7-sequence-diagrams)
8. [Deployment Diagrams](#8-deployment-diagrams)
9. [Architecture Justification](#9-architecture-justification)

---

## 1. Architecture Selection

### Selected Architecture: **Monolithic Architecture with Modular Design**

FairDeal employs a **Monolithic Architecture** with clear internal modularization. This architecture choice is justified by the following factors:

#### Why Monolithic?

1. **Single Deployment Unit**: The entire backend is deployed as one cohesive application, simplifying deployment and operations.

2. **Shared Data Access**: All modules share the same database connections (SQLite/PostgreSQL and ChromaDB), enabling efficient data access without network overhead.

3. **Development Simplicity**: For a small to medium-sized team, a monolithic architecture reduces complexity in development, testing, and debugging.

4. **Performance**: Direct in-memory function calls between modules eliminate network latency that would exist in microservices.

5. **Transaction Management**: ACID transactions across multiple database operations are straightforward in a monolithic system.

#### Modular Design Principles

While monolithic, the system is organized into clear modules:

- **API Layer**: FastAPI routes and request handling
- **Service Layer**: Business logic (analysis, extraction, statistics)
- **Data Layer**: Database access and persistence
- **Parser Layer**: Document parsing and OCR
- **LLM Integration Layer**: External AI service integration

This modular structure allows for future migration to microservices if needed, while maintaining simplicity for the current scale.

---

## 2. Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FairDeal Backend                         │
│                  (Monolithic Application)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   API Layer  │  │ Service Layer│  │  Data Layer  │    │
│  │              │  │              │  │              │    │
│  │ - Auth API   │  │ - Analysis   │  │ - SQLAlchemy │    │
│  │ - Contract   │  │ - Extraction │  │ - ChromaDB   │    │
│  │   API        │  │ - Statistics │  │ - File I/O    │    │
│  │ - Profile    │  │ - RAG        │  │              │    │
│  │   API        │  │ - Chatbot    │  │              │    │
│  │ - Debug API  │  │              │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │ Parser Layer │  │ LLM Layer    │                       │
│  │              │  │              │                       │
│  │ - PDF        │  │ - Gemini API │                       │
│  │ - DOCX       │  │ - Embeddings │                       │
│  │ - OCR        │  │              │                       │
│  └──────────────┘  └──────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │PostgreSQL│         │ ChromaDB│         │File System│
    │/ SQLite  │         │(Vectors) │         │(Contracts)│
    └─────────┘         └─────────┘         └─────────┘
```

### Architecture Layers

#### 1. **Presentation Layer (API)**
- FastAPI REST endpoints
- Request validation and authentication
- Response serialization
- Error handling

#### 2. **Business Logic Layer (Services)**
- Contract analysis orchestration
- Metadata extraction
- Statistical computation
- RAG retrieval
- Chatbot logic

#### 3. **Data Access Layer**
- Database ORM (SQLAlchemy)
- Vector database client (ChromaDB)
- File system operations
- Caching (if implemented)

#### 4. **Integration Layer**
- LLM API clients
- External service adapters
- Rate limiting and retry logic

---

## 3. Use Case Diagrams

### 3.1 System Use Case Diagram

```mermaid
graph TB
    User[User]
    Admin[Administrator]
    System[FairDeal System]
    
    User -->|Register/Login| Auth[Authentication]
    User -->|Upload Contract| Upload[Upload Contract]
    User -->|View Analysis| Analysis[View Analysis Results]
    User -->|Chat with AI| Chat[AI Chatbot]
    User -->|View Profile| Profile[View Profile & History]
    
    Admin -->|Ingest Contracts| Ingest[Ingest Contracts to KB]
    Admin -->|Monitor System| Monitor[System Monitoring]
    
    System -->|Extract Text| Extract[Text Extraction]
    System -->|Analyze Contract| Analyze[Contract Analysis]
    System -->|Compare Market| Compare[Market Comparison]
    System -->|Generate Report| Report[Generate Report]
    
    style User fill:#e1f5ff
    style Admin fill:#fff4e1
    style System fill:#e8f5e9
```

### 3.2 Contract Analysis Use Case

```mermaid
graph LR
    User[User] -->|1. Upload| Upload[Upload Contract File]
    Upload -->|2. Parse| Parse[Parse Document]
    Parse -->|3. Extract| Extract[Extract Metadata]
    Extract -->|4. Compare| Compare[Compare with Market]
    Compare -->|5. Score| Score[Calculate Fairness Score]
    Score -->|6. Generate| Generate[Generate Insights]
    Generate -->|7. Display| Display[Display Results]
    
    style User fill:#e1f5ff
    style Display fill:#c8e6c9
```

### 3.3 Administrator Use Cases

```mermaid
graph TB
    Admin[Administrator] -->|1. Upload| Upload[Upload Raw Contracts]
    Upload -->|2. Process| Process[Process Contracts]
    Process -->|3. Extract| Extract[Extract Metadata via LLM]
    Extract -->|4. Chunk| Chunk[Chunk into Clauses]
    Chunk -->|5. Embed| Embed[Generate Embeddings]
    Embed -->|6. Store| Store[Store in Knowledge Base]
    Store -->|7. Compute| Compute[Compute Statistics]
    
    style Admin fill:#fff4e1
    style Store fill:#c8e6c9
```

---

## 4. Class Diagrams

### 4.1 Core Domain Classes

```mermaid
classDiagram
    class User {
        +String id
        +String email
        +String name
        +String hashed_password
        +DateTime created_at
        +bool is_active
        +login()
        +logout()
    }
    
    class ContractAnalysis {
        +String id
        +String user_id
        +String contract_filename
        +int fairness_score
        +String contract_type
        +String industry
        +String role
        +String location
        +int salary
        +int notice_period_days
        +String analysis_result_json
        +DateTime created_at
    }
    
    class ContractMetadata {
        +ExtractedField contract_type
        +ExtractedField industry
        +ExtractedField role
        +ExtractedField location
        +ExtractedField salary
        +ExtractedField notice_period_days
        +ExtractedField non_compete
        +List termination_clauses
        +List benefits
        +List risky_clauses
    }
    
    class ExtractedField {
        +T value
        +float confidence
        +String source_text
        +String explanation
    }
    
    class AnalysisResult {
        +int fairness_score
        +ContractMetadata contract_metadata
        +Dict percentile_rankings
        +List red_flags
        +List favorable_terms
        +List negotiation_priorities
        +int similar_contracts_count
        +Dict detailed_explanation
        +String narration
    }
    
    User "1" --> "*" ContractAnalysis : owns
    ContractAnalysis "1" --> "1" AnalysisResult : contains
    AnalysisResult "1" --> "1" ContractMetadata : contains
    ContractMetadata "*" --> "1" ExtractedField : uses
```

### 4.2 Service Layer Classes

```mermaid
classDiagram
    class AnalysisService {
        -PDFParser pdf_parser
        -DOCXParser docx_parser
        -FastExtractionService fast_extraction
        -LLMService llm_service
        -RAGService rag_service
        -StatsService stats_service
        -ClauseMatcher clause_matcher
        +analyze_contract(file_content, filename) AnalysisResult
        -_parse_file() String
        -_compute_percentiles() Dict
        -_compute_fairness_score() int
        -_generate_narration() String
    }
    
    class FastExtractionService {
        -List salary_patterns
        -List notice_period_patterns
        -Dict contract_type_keywords
        +extract_metadata(text) ContractMetadata
        -_extract_salary() ExtractedField
        -_extract_notice_period() ExtractedField
        -_extract_contract_type() ExtractedField
    }
    
    class LLMService {
        -str provider
        -str model
        -GenAI client
        +extract_contract_metadata(text) ContractMetadata
        +_call_llm(prompt, format) str
        -_clean_json_response() str
    }
    
    class RAGService {
        -ChromaClient chroma_client
        +retrieve_similar_contracts(query, filters) List
        +ingest_contract(text, metadata) str
    }
    
    class StatsService {
        +get_percentile(field, value, filters) float
        +get_market_stats(field, filters) Dict
        -_get_all_contracts_metadata() List
        -_extract_value() Any
    }
    
    class ClauseMatcher {
        +match_clauses(metadata, percentiles) Dict
        -_check_salary_red_flags() List
        -_check_notice_period_flags() List
    }
    
    AnalysisService --> FastExtractionService
    AnalysisService --> LLMService
    AnalysisService --> RAGService
    AnalysisService --> StatsService
    AnalysisService --> ClauseMatcher
```

### 4.3 Data Access Layer Classes

```mermaid
classDiagram
    class Database {
        +Session get_db()
        +init_db()
    }
    
    class ChromaClient {
        -str db_path
        -str collection_name
        -PersistentClient client
        +add_documents(ids, texts, embeddings, metadata)
        +query(query_text, n_results, filters) List
        +get_collection_stats() Dict
    }
    
    class PDFParser {
        +extract_text(file_path) String
        -_extract_text_with_ocr() String
        -_enhance_image_for_ocr() Image
    }
    
    class DOCXParser {
        +extract_text(file_path) String
    }
    
    Database --> User
    Database --> ContractAnalysis
    ChromaClient --> ContractAnalysis
```

---

## 5. Data Flow Diagrams (DFD)

### 5.1 Level 0 DFD (Context Diagram)

```mermaid
graph TB
    User[User] -->|Contract File| System[FairDeal System]
    Admin[Administrator] -->|Raw Contracts| System
    System -->|Analysis Results| User
    System -->|Knowledge Base| KB[(Knowledge Base)]
    System -->|User Data| DB[(Database)]
    LLM[LLM API] -->|Metadata/Embeddings| System
    System -->|Queries| LLM
```

### 5.2 Level 1 DFD (System Decomposition)

```mermaid
graph TB
    User[User] -->|1. Upload| Upload[1.0 Upload Contract]
    Upload -->|File| Parse[2.0 Parse Document]
    Parse -->|Text| Extract[3.0 Extract Metadata]
    Extract -->|Metadata| Compare[4.0 Compare with Market]
    Compare -->|Stats| Score[5.0 Calculate Score]
    Score -->|Results| Store[6.0 Store Analysis]
    Store -->|Results| User
    
    Admin[Admin] -->|Raw Files| Ingest[7.0 Ingest Contracts]
    Ingest -->|Text| Process[8.0 Process & Embed]
    Process -->|Vectors| KB[(Knowledge Base)]
    Process -->|Metadata| Stats[9.0 Compute Statistics]
    Stats -->|Stats| KB
    
    Extract -.->|Fallback| LLM[LLM Service]
    Process -->|Embeddings| LLM
    LLM -->|Vectors| Process
    
    Compare -->|Query| KB
    KB -->|Similar Contracts| Compare
```

### 5.3 Level 2 DFD (Contract Analysis Process)

```mermaid
graph TB
    File[Contract File] -->|Bytes| Parse[2.1 Parse File]
    Parse -->|Text| FastExtract[2.2 Fast Extraction]
    FastExtract -->|Metadata| Check[2.3 Quality Check]
    Check -->|Incomplete| LLMExtract[2.4 LLM Extraction]
    Check -->|Complete| Percentile[2.5 Compute Percentiles]
    LLMExtract -->|Metadata| Percentile
    Percentile -->|Rankings| Match[2.6 Match Clauses]
    Match -->|Insights| Score[2.7 Calculate Score]
    Score -->|Final Result| Store[2.8 Store Result]
    
    Parse -->|Text| RAG[2.9 RAG Retrieval]
    RAG -->|Similar| Percentile
    KB[(Knowledge Base)] -->|Query| RAG
```

---

## 6. Component Diagrams

### 6.1 System Components

```mermaid
graph TB
    subgraph "Frontend"
        React[React Application]
    end
    
    subgraph "Backend Application"
        API[API Layer]
        Auth[Authentication Module]
        Analysis[Analysis Module]
        Ingestion[Ingestion Module]
        Chatbot[Chatbot Module]
    end
    
    subgraph "Services"
        Extract[Extraction Service]
        Stats[Statistics Service]
        RAG[RAG Service]
        LLM[LLM Service]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL/SQLite)]
        VectorDB[(ChromaDB)]
        FileSystem[File System]
    end
    
    subgraph "External"
        Gemini[Google Gemini API]
    end
    
    React -->|HTTP/REST| API
    API --> Auth
    API --> Analysis
    API --> Ingestion
    API --> Chatbot
    
    Analysis --> Extract
    Analysis --> Stats
    Analysis --> RAG
    Ingestion --> Extract
    Ingestion --> RAG
    Chatbot --> LLM
    
    Extract --> LLM
    RAG --> LLM
    LLM --> Gemini
    
    Auth --> DB
    Analysis --> DB
    Analysis --> VectorDB
    Ingestion --> VectorDB
    Ingestion --> FileSystem
    Analysis --> FileSystem
```

### 6.2 Module Dependencies

```mermaid
graph LR
    API[API Layer] --> Services[Service Layer]
    Services --> Data[Data Access Layer]
    Services --> Parser[Parser Layer]
    Services --> LLM[LLM Integration]
    Data --> DB[(Database)]
    Data --> VectorDB[(ChromaDB)]
    Parser --> FileSystem[File System]
    LLM --> External[External APIs]
    
    style API fill:#e1f5ff
    style Services fill:#fff4e1
    style Data fill:#e8f5e9
```

---

## 7. Sequence Diagrams

### 7.1 Contract Analysis Sequence

```mermaid
sequenceDiagram
    participant User
    participant API
    participant AnalysisService
    participant FastExtract
    participant StatsService
    participant ClauseMatcher
    participant LLMService
    participant Database
    participant ChromaDB
    
    User->>API: POST /api/contracts/analyze (file)
    API->>AnalysisService: analyze_contract(file_content, filename)
    
    AnalysisService->>AnalysisService: _parse_file() → text
    
    AnalysisService->>FastExtract: extract_metadata(text)
    FastExtract-->>AnalysisService: ContractMetadata
    
    alt Fast extraction incomplete
        AnalysisService->>LLMService: extract_contract_metadata(text)
        LLMService-->>AnalysisService: ContractMetadata (complete)
    end
    
    AnalysisService->>StatsService: get_percentile(salary, filters)
    StatsService->>ChromaDB: Query metadata
    ChromaDB-->>StatsService: Contract data
    StatsService-->>AnalysisService: Percentile rankings
    
    AnalysisService->>ClauseMatcher: match_clauses(metadata, percentiles)
    ClauseMatcher-->>AnalysisService: Red flags, favorable terms
    
    AnalysisService->>AnalysisService: _compute_fairness_score()
    AnalysisService->>LLMService: _generate_narration() (optional)
    LLMService-->>AnalysisService: Narration text
    
    AnalysisService->>Database: Store analysis result
    Database-->>AnalysisService: Analysis ID
    
    AnalysisService-->>API: AnalysisResult
    API-->>User: JSON response with results
```

### 7.2 Contract Ingestion Sequence

```mermaid
sequenceDiagram
    participant Admin
    participant API
    participant IngestionService
    participant Parser
    participant LLMService
    participant EmbeddingService
    participant ChromaDB
    participant FileSystem
    
    Admin->>API: POST /api/contracts/ingest (file)
    API->>IngestionService: ingest_contract(file_content, filename)
    
    IngestionService->>Parser: extract_text(file_path)
    Parser-->>IngestionService: Contract text
    
    IngestionService->>LLMService: extract_contract_metadata(text)
    LLMService-->>IngestionService: ContractMetadata
    
    IngestionService->>IngestionService: chunk_text(text) → chunks
    
    loop For each chunk
        IngestionService->>EmbeddingService: generate_embedding(chunk)
        EmbeddingService-->>IngestionService: Vector embedding
    end
    
    IngestionService->>ChromaDB: add_documents(ids, chunks, embeddings, metadata)
    ChromaDB-->>IngestionService: Success
    
    IngestionService->>FileSystem: Save metadata JSON
    FileSystem-->>IngestionService: Success
    
    IngestionService-->>API: Ingestion result
    API-->>Admin: Success response
```

### 7.3 User Authentication Sequence

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AuthService
    participant Database
    
    User->>Frontend: Enter credentials
    Frontend->>API: POST /api/auth/login (email, password)
    
    API->>AuthService: authenticate_user(email, password)
    AuthService->>Database: Query user by email
    Database-->>AuthService: User record
    
    AuthService->>AuthService: Verify password hash
    AuthService->>AuthService: create_access_token(user_id)
    AuthService-->>API: JWT token
    
    API-->>Frontend: {access_token, token_type}
    Frontend->>Frontend: Store token
    Frontend-->>User: Redirect to dashboard
```

### 7.4 RAG Retrieval Sequence

```mermaid
sequenceDiagram
    participant AnalysisService
    participant RAGService
    participant EmbeddingService
    participant ChromaDB
    participant LLMService
    
    AnalysisService->>RAGService: retrieve_similar_contracts(query, filters)
    
    RAGService->>EmbeddingService: generate_embedding(query)
    EmbeddingService-->>RAGService: Query embedding vector
    
    RAGService->>ChromaDB: query(embedding, n_results=5, filters)
    ChromaDB-->>RAGService: Similar contract chunks
    
    RAGService-->>AnalysisService: List of similar contracts
```

---

## 8. Deployment Diagrams

### 8.1 System Deployment Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        Mobile[Mobile App - Future]
    end
    
    subgraph "Application Server"
        subgraph "FairDeal Backend"
            API[FastAPI Application]
            Services[Service Modules]
            Workers[Background Workers]
        end
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL Database)]
        VectorDB[(ChromaDB Vector Store)]
        FileStorage[File Storage]
    end
    
    subgraph "External Services"
        Gemini[Google Gemini API]
    end
    
    Browser -->|HTTPS| API
    Mobile -->|HTTPS| API
    
    API --> Services
    Services --> DB
    Services --> VectorDB
    Services --> FileStorage
    Services --> Gemini
    
    Workers --> DB
    Workers --> VectorDB
    Workers --> FileStorage
```

### 8.2 Production Deployment

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx/Cloudflare]
    end
    
    subgraph "Application Servers"
        App1[Backend Server 1<br/>Uvicorn]
        App2[Backend Server 2<br/>Uvicorn]
    end
    
    subgraph "Database Cluster"
        Primary[(PostgreSQL Primary)]
        Replica[(PostgreSQL Replica)]
    end
    
    subgraph "Storage"
        VectorStore[(ChromaDB)]
        FileSystem[Object Storage/S3]
    end
    
    subgraph "External"
        Gemini[Gemini API]
    end
    
    Users[Users] -->|HTTPS| LB
    LB --> App1
    LB --> App2
    
    App1 --> Primary
    App2 --> Primary
    App1 --> Replica
    App2 --> Replica
    
    App1 --> VectorStore
    App2 --> VectorStore
    App1 --> FileSystem
    App2 --> FileSystem
    
    App1 --> Gemini
    App2 --> Gemini
```

### 8.3 Development Deployment

```mermaid
graph TB
    Developer[Developer Machine]
    
    subgraph "Local Development"
        Backend[FastAPI Backend<br/>localhost:8000]
        Frontend[React Frontend<br/>localhost:5173]
        SQLite[(SQLite Database)]
        ChromaDB[(ChromaDB Local)]
        Files[Local File System]
    end
    
    subgraph "External"
        Gemini[Gemini API<br/>Cloud]
    end
    
    Developer --> Backend
    Developer --> Frontend
    
    Frontend -->|API Calls| Backend
    Backend --> SQLite
    Backend --> ChromaDB
    Backend --> Files
    Backend --> Gemini
```

---

## 9. Architecture Justification

### 9.1 Why Monolithic Architecture?

#### Advantages for FairDeal

1. **Simplicity**
   - Single codebase reduces complexity
   - Easier to understand and maintain
   - Faster development cycles
   - Simplified testing and debugging

2. **Performance**
   - No network overhead between modules
   - Direct function calls are faster than HTTP/RPC
   - Shared memory for caching
   - Efficient database connection pooling

3. **Transaction Management**
   - ACID transactions across multiple operations
   - Consistent data state
   - Easier rollback on errors

4. **Deployment**
   - Single deployment unit
   - Easier versioning and rollback
   - Reduced operational complexity

5. **Resource Efficiency**
   - Lower memory footprint
   - No service mesh overhead
   - Efficient resource utilization

#### When to Consider Microservices

FairDeal would benefit from microservices if:
- Team size grows beyond 10 developers
- Different modules need independent scaling
- Different deployment schedules are required
- Polyglot programming is needed
- Fault isolation becomes critical

Currently, these conditions are not met, making monolithic architecture the optimal choice.

### 9.2 Modular Design Benefits

While monolithic, the system maintains clear module boundaries:

1. **API Layer**: Isolated from business logic
2. **Service Layer**: Reusable business logic
3. **Data Layer**: Abstracted database access
4. **Integration Layer**: External service adapters

This modularity enables:
- Future migration to microservices if needed
- Independent testing of modules
- Clear separation of concerns
- Easier code maintenance

### 9.3 Comparison with Other Architectures

#### Monolithic vs. Microservices

| Aspect | Monolithic (FairDeal) | Microservices |
|--------|----------------------|---------------|
| **Complexity** | Low | High |
| **Deployment** | Single unit | Multiple services |
| **Scaling** | Vertical | Horizontal (per service) |
| **Latency** | Low (in-process) | Higher (network) |
| **Team Size** | Small-medium | Large |
| **Current Fit** | ✅ Optimal | ❌ Over-engineered |

#### Monolithic vs. Serverless

| Aspect | Monolithic (FairDeal) | Serverless |
|--------|----------------------|------------|
| **Cold Starts** | None | Possible |
| **State Management** | In-memory | Stateless |
| **Long-Running Tasks** | Supported | Limited |
| **Cost** | Predictable | Pay-per-use |
| **Current Fit** | ✅ Optimal | ❌ Not suitable |

#### Monolithic vs. Event-Driven

| Aspect | Monolithic (FairDeal) | Event-Driven |
|--------|----------------------|--------------|
| **Coupling** | Tight | Loose |
| **Complexity** | Low | High |
| **Real-time** | Request-response | Async events |
| **Current Fit** | ✅ Optimal | ❌ Unnecessary |

### 9.4 Future Evolution Path

The current monolithic architecture can evolve:

**Phase 1 (Current)**: Monolithic with modules
- Single deployment
- Clear module boundaries
- Shared database

**Phase 2 (If Needed)**: Modular Monolith
- Separate modules with clear interfaces
- Still single deployment
- Easier to extract services later

**Phase 3 (If Scale Demands)**: Microservices
- Extract ingestion service (offline processing)
- Extract analysis service (runtime processing)
- Extract chatbot service (optional LLM)
- Shared data layer via APIs

The current architecture supports this evolution without requiring a complete rewrite.

---

## 10. Architecture Patterns Used

### 10.1 Layered Architecture

The system follows a layered architecture pattern:

```
┌─────────────────────┐
│   Presentation      │  API Layer
├─────────────────────┤
│   Business Logic    │  Service Layer
├─────────────────────┤
│   Data Access       │  Data Layer
├─────────────────────┤
│   Infrastructure    │  External Services
└─────────────────────┘
```

### 10.2 Service-Oriented Architecture (Internal)

While monolithic, the system uses service-oriented principles internally:

- **AnalysisService**: Orchestrates contract analysis
- **ExtractionService**: Handles metadata extraction
- **StatsService**: Computes statistics
- **RAGService**: Manages vector retrieval
- **ChatbotService**: Handles AI conversations

Each service has a single responsibility and clear interface.

### 10.3 Repository Pattern

Data access follows the repository pattern:

- **Database**: SQLAlchemy ORM abstracts database access
- **ChromaDB**: ChromaClient abstracts vector database
- **File System**: Parser classes abstract file operations

This enables:
- Easy testing (mock repositories)
- Database-agnostic code
- Clear data access boundaries

### 10.4 Strategy Pattern

The system uses strategy pattern for:

- **Extraction Strategy**: Fast extraction vs. LLM extraction
- **Parser Strategy**: PDF parser vs. DOCX parser
- **LLM Strategy**: Different LLM providers (currently Gemini)

This allows runtime selection of strategies based on context.

---

## 11. Non-Functional Requirements

### 11.1 Performance

- **Response Time**: < 4 seconds for contract analysis
- **Throughput**: 10+ concurrent analyses
- **Scalability**: Vertical scaling (add CPU/RAM)

### 11.2 Reliability

- **Availability**: 99% uptime target
- **Fault Tolerance**: Graceful degradation if LLM unavailable
- **Error Handling**: Comprehensive error messages

### 11.3 Security

- **Authentication**: JWT-based authentication
- **Authorization**: User-scoped data access
- **Data Protection**: Encrypted passwords, secure file storage

### 11.4 Maintainability

- **Code Organization**: Clear module structure
- **Documentation**: Comprehensive inline and external docs
- **Testing**: Unit tests for critical paths

---

## 12. Conclusion

FairDeal employs a **Monolithic Architecture with Modular Design** that provides:

1. **Simplicity**: Easy to develop, test, and deploy
2. **Performance**: Fast in-process communication
3. **Maintainability**: Clear module boundaries
4. **Scalability**: Can evolve to microservices if needed
5. **Cost-Effectiveness**: Lower operational overhead

This architecture choice is optimal for the current scale and requirements, while providing a clear path for future evolution if needed.

---

## Appendix: Diagram Tools

All diagrams in this document are created using:
- **Mermaid.js**: For flowcharts, sequence diagrams, class diagrams
- **ASCII Art**: For simple structural diagrams
- **Standard UML**: Following UML 2.5 specifications

Diagrams can be rendered in:
- GitHub/GitLab (native Mermaid support)
- Markdown viewers with Mermaid plugin
- Documentation tools (Docusaurus, MkDocs)
- Online Mermaid editors

---

**Document End**

