# Islamic Finance Standards Enhancement System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Challenge 3 Submission: AI-Powered Islamic Finance Standards Enhancement Platform**

## Overview

The Islamic Finance Standards Enhancement System is a multi-agent, event-driven architecture designed to improve AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions) standards through AI-driven analysis and enhancement proposals. The system processes standard documents, identifies ambiguities, generates enhancement proposals, and validates them against Shariah principles.

## Quick Start Guide

### 1. Clone the Repository

```bash
git clone https://github.com/Faycall1l/IsDBI-StandardsEnhancement.git
cd IsDBI-StandardsEnhancement
```

### 2. Set Up Environment

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Your OpenAI API Key

```bash
python set_api_key.py
```

### 4. Initialize the Database

```bash
python init_db.py
```

### 5. Run the System

```bash
python integrated_platform.py
```

### 6. Access the Web Interface

Open your browser and navigate to: http://localhost:5001

### 7. Run Tests (Optional)

```bash
python test_system.py
```

## Key Features & Demo Workflow

### Key Features

1. **Document Processing**
   - Upload AAOIFI standard documents (FAS 4, FAS 10, FAS 32)
   - Extract structured data including definitions, accounting treatments, and transaction structures
   - Identify ambiguities in the standards

2. **Enhancement Generation**
   - Generate improvement proposals for standards using AI
   - Provide rationale for suggested enhancements
   - Support web search for additional context

3. **Shariah Validation**
   - Validate enhancement proposals against Islamic finance principles
   - Provide compliance scores and detailed feedback
   - Flag potential Shariah compliance issues

4. **Audit & Traceability**
   - Track all system events and user actions
   - Maintain immutable audit logs
   - Ensure transparency in the enhancement process

### Demo Workflow

1. **Process a Standard Document**:
   - Navigate to "Process Document" in the web interface
   - Select a standard (e.g., FAS 4 - Musharaka)
   - Upload the PDF document from the `data/standards` directory
   - View the extracted structured data

2. **Generate Enhancement Proposals**:
   - Navigate to "Generate Enhancement"
   - Select a standard or paste standard text
   - Click "Generate Enhancement"
   - Review the AI-generated enhancement proposal and rationale

3. **Review and Validate Proposals**:
   - Navigate to "Proposals"
   - View all enhancement proposals
   - Click on a proposal to see validation results
   - Add comments or vote on proposals

4. **Monitor System Events**:
   - Navigate to "System Events"
   - View all events flowing through the system
   - Check audit logs for compliance tracking

## System Architecture

The system is built on a multi-layered architecture with four primary layers:

1. **Use Case Scenarios (Journal Generator)** - Generates accounting journal entries based on standards
2. **Reverse Transactions (Error Corrector)** - Identifies and corrects errors in transaction processing
3. **Standards Enhancement (Current Focus)** - Analyzes and improves AAOIFI standards
4. **Custom Compliance Advisor** - Provides tailored compliance guidance

### Key Components

- **Event-Driven Communication** - Simulates Apache Kafka for asynchronous communication between agents
- **Knowledge Graph** - Neo4j database storing standards, concepts, principles, and relationships
- **Audit Logging** - Simulates Hyperledger Fabric for immutable audit trails
- **Shariah Compliance Validation** - Rule-based validation of enhancement proposals

### Multi-Agent Architecture

The system employs three specialized agents:

1. **Document Agent** - Processes AAOIFI standards PDFs and extracts structured data:
   - Definitions
   - Accounting treatments
   - Transaction structures
   - Ambiguities

2. **Enhancement Agent** - Generates improvement proposals using chain-of-thought reasoning:
   - Analyzes standard text
   - Identifies areas for improvement
   - Generates enhancement proposals
   - Provides rationale for changes

3. **Validation Agent** - Reviews proposals against Shariah principles:
   - Validates enhancements against Islamic finance principles
   - Provides detailed feedback
   - Assigns compliance scores
   - Recommends approval or revision

### System Integration

All components are connected through:

1. **Shared Database** - SQLite database storing standards, definitions, accounting treatments, transaction structures, ambiguities, enhancement proposals, validations, comments, votes, events, and audit logs.

2. **File Manager** - Handles document storage and sharing between components, including saving and retrieving standard documents, enhancement proposals, validation results, and event logs.

3. **Event Bus** - Enables asynchronous communication between agents, allowing for a decoupled architecture where components can publish and subscribe to events.

4. **System Integrator** - Orchestrates the flow of data and events between all components, ensuring seamless integration.

## Technical Specifications

### Backend

- **Language**: Python 3.8+
- **Web Framework**: Flask
- **Database**: SQLite (with Neo4j for knowledge graph)
- **Event System**: Custom implementation simulating Kafka
- **Audit Logging**: Custom implementation simulating Hyperledger Fabric
- **PDF Processing**: PyPDF2, pdfplumber
- **NLP Processing**: spaCy, NLTK
- **AI Integration**: OpenAI API

### Frontend

- **Framework**: Flask templates with Bootstrap 5
- **JavaScript**: Vanilla JS with jQuery
- **Visualization**: Chart.js for analytics

### Data Flow

1. **Document Processing**:
   - PDF document uploaded through web interface
   - Document Agent extracts structured data
   - Extracted data stored in shared database and knowledge graph
   - Event published to notify other components

2. **Enhancement Generation**:
   - Enhancement Agent subscribes to document processing events
   - Analyzes standard text and identifies improvement areas
   - Generates enhancement proposals
   - Stores proposals in shared database
   - Event published to notify validation

3. **Proposal Validation**:
   - Validation Agent subscribes to enhancement generation events
   - Reviews proposals against Shariah principles
   - Provides validation feedback
   - Updates proposal status
   - Event published to notify web interface

4. **User Interaction**:
   - Web interface displays standards, proposals, and validations
   - Users can vote on proposals, add comments, and approve/reject
   - Actions trigger events for audit logging
   - Dashboard provides analytics on enhancement process

## Target Standards

The system is designed to work with AAOIFI standards, with initial focus on:

- **FAS 4**: Musharaka Financing
- **FAS 10**: Istisna'a and Parallel Istisna'a
- **FAS 32**: Ijarah and Ijarah Muntahia Bittamleek

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/Faycall1l/IsDBI-StandardsEnhancement.git
   cd IsDBI-StandardsEnhancement
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file to add your OpenAI API key.

5. Initialize the database:
   ```
   python init_db.py
   ```

6. Run the application:
   ```
   python integrated_platform.py
   ```

7. Access the web interface:
   Open your browser and navigate to `http://localhost:5001`

## Running Tests

The system includes comprehensive tests to verify functionality:

1. Run all tests:
   ```
   python -m pytest tests/
   ```

2. Run specific test categories:
   ```
   python -m pytest tests/test_document_agent.py
   python -m pytest tests/test_enhancement_agent.py
   python -m pytest tests/test_validation_agent.py
   python -m pytest tests/test_integration.py
   ```

3. Run end-to-end test with real documents:
   ```
   python test_system.py
   ```

## Usage Guide

### Processing a Standard Document

1. Navigate to the "Process Document" page
2. Select a standard from the dropdown (FAS 4, FAS 10, FAS 32)
3. Upload the PDF document
4. Click "Process Document"
5. View the extracted data and generated enhancements

### Generating Enhancements

1. Navigate to the "Generate Enhancement" page
2. Select a standard or paste standard text
3. Click "Generate Enhancement"
4. View the generated enhancement proposal

### Reviewing Proposals

1. Navigate to the "Proposals" page
2. Browse all enhancement proposals
3. Filter by status (pending, validated, approved, rejected)
4. Click on a proposal to view details
5. Add comments or vote on proposals

### Monitoring System Events

1. Navigate to the "System Events" page
2. View all events flowing through the system
3. Filter by event type or component
4. View audit logs for compliance tracking

## Project Structure

```
IsDBI-StandardsEnhancement/
├── IslamicFinanceStandardsAI/        # Main package
│   ├── agents/                       # Agent implementations
│   │   ├── document_agent/           # Document processing agent
│   │   ├── enhancement_agent/        # Enhancement generation agent
│   │   └── validation_agent/         # Validation agent
│   ├── database/                     # Database implementations
│   │   ├── knowledge_graph.py        # Neo4j knowledge graph
│   │   └── shared_database.py        # SQLite shared database
│   ├── integration/                  # Integration components
│   │   ├── event_bus.py              # Event bus for communication
│   │   └── system_integrator.py      # System orchestration
│   ├── utils/                        # Utility modules
│   │   ├── audit_logger.py           # Audit logging
│   │   ├── file_manager.py           # File management
│   │   └── web_retriever.py          # Web search for enhancements
│   └── frontend/                     # Frontend components
│       ├── templates/                # HTML templates
│       └── static/                   # CSS, JS, images
├── data/                             # Data storage
│   ├── standards/                    # Standard documents
│   ├── enhancements/                 # Enhancement proposals
│   └── validations/                  # Validation results
├── tests/                            # Test suite
│   ├── test_document_agent.py        # Document agent tests
│   ├── test_enhancement_agent.py     # Enhancement agent tests
│   ├── test_validation_agent.py      # Validation agent tests
│   └── test_integration.py           # Integration tests
├── integrated_platform.py            # Main application entry point
├── test_system.py                    # End-to-end test script
├── init_db.py                        # Database initialization
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Sample Test Documents

The repository includes sample AAOIFI standard documents for testing:

- `data/standards/FAS4_Musharaka.pdf`
- `data/standards/FAS10_Istisna.pdf`
- `data/standards/FAS32_Ijarah.pdf`
