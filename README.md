# Islamic Finance Standards Enhancement System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](https://islamic-finance-standards.readthedocs.io/)

> **AI-Powered Islamic Finance Standards Enhancement Platform**

## Overview

The Islamic Finance Standards Enhancement System is an advanced multi-agent platform designed to analyze, validate, and enhance Islamic finance standards with state-of-the-art AI and rule-based validation. The system provides comprehensive tools for processing standard documents, identifying ambiguities, generating enhancement proposals, and validating them against Shariah principles using advanced mathematical models and compliance checks.

## 🚀 Key Features

### Advanced Shariah Compliance Validation
- **Riba Detection**: Identifies interest-based terms and structures using pattern matching and financial analysis
- **Gharar Analysis**: Detects excessive uncertainty in contract terms using statistical models
- **Maysir Detection**: Flags gambling/speculative elements with advanced pattern recognition
- **Haram Activities**: Scans for prohibited elements in financial contracts
- **Contract Duration**: Validates contract terms against Shariah-compliant timeframes

### Advanced Financial Analysis
- **Arbitrage Detection**: Identifies risk-free profit opportunities using statistical methods
- **Risk Metrics**: Calculates Sharpe and Sortino ratios for performance evaluation
- **Volatility Analysis**: Detects volatility clustering and fat tails in return distributions
- **Financial Ratios**: Validates against Shariah-compliant thresholds and industry benchmarks

### Document Processing & Enhancement
- **Multi-format Support**: Processes PDF, DOCX, and plain text documents
- **Semantic Analysis**: Extracts key terms, definitions, and accounting treatments
- **Ambiguity Detection**: Identifies unclear or contradictory clauses
- **Enhancement Proposals**: Generates AI-powered suggestions for standard improvements

### Knowledge Integration
- **Neo4j Knowledge Graph**: Stores and retrieves structured data about Islamic finance standards
- **RAG Implementation**: Local embeddings for efficient document retrieval
- **Regulatory Updates**: Tracks changes in Islamic finance regulations and standards

## 🛠️ Quick Start Guide

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

# Install development dependencies (optional)
pip install -r requirements-dev.txt
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
# Start the main application
python integrated_platform.py

# Or run with Gunicorn for production
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### 6. Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_shariah_validation.py -v
```

### 6. Access the Web Interface

Open your browser and navigate to: http://localhost:5001

### 7. Testing the System Workflow

Test the system components with the correct parameters (requires Gemini API key):

```bash
# Set your Gemini API key
export GEMINI_API_KEY=your_api_key_here

# Test document processing component
python IslamicFinanceStandardsAI/test_components.py --component document --standard-id FAS4 --file ./data/standards/FAS4_Musharaka.pdf

# Test the full workflow
python IslamicFinanceStandardsAI/test_components.py --component workflow --standard-id FAS4 --file ./data/standards/FAS4_Musharaka.pdf
```

You can also test with different standards:

```bash
# Test with FAS 10 (Istisna'a)
python IslamicFinanceStandardsAI/test_components.py --component document --standard-id FAS10 --file ./data/standards/FAS10_Istisna.pdf

# Test with FAS 32 (Ijarah)
python IslamicFinanceStandardsAI/test_components.py --component document --standard-id FAS32 --file ./data/standards/FAS32_Ijarah.pdf
```

All test results are displayed in the console output and can be redirected to files for analysis:

```bash
python IslamicFinanceStandardsAI/test_components.py --component document --standard-id FAS4 --file ./data/standards/FAS4_Musharaka.pdf > document_test_results.log
```

## 🏗️ System Architecture

The system is built on a robust multi-layered architecture with advanced validation capabilities:

### Core Components

1. **Document Processing Layer**
   - Handles document ingestion and parsing
   - Extracts structured data from various formats
   - Identifies key elements and potential issues

2. **Validation Layer**
   - Implements Shariah compliance checks
   - Applies advanced financial analysis
   - Validates contract terms against Islamic principles

3. **Knowledge Layer**
   - Neo4j knowledge graph for structured data
   - Document embedding for semantic search
   - Regulatory update tracking

4. **API Layer**
   - RESTful endpoints for system integration
   - WebSocket support for real-time updates
   - Authentication and authorization

### Advanced Validation Pipeline

1. **Input Processing**
   - Document parsing and text extraction
   - Language detection and translation
   - Term extraction and normalization

2. **Compliance Analysis**
   - Riba detection and analysis
   - Gharar assessment
   - Maysir identification
   - Contract structure validation

3. **Financial Analysis**
   - Risk assessment
   - Return analysis
   - Volatility modeling
   - Performance metrics

4. **Reporting**
   - Compliance scoring
   - Issue categorization
   - Recommendation generation
   - Audit trail

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

## 🤖 Multi-Agent Architecture

The system employs a sophisticated multi-agent architecture with specialized components:

### Core Agents

1. **Document Agent**
   - **Input Processing**: Handles document ingestion and parsing
   - **Text Extraction**: Extracts text from various formats (PDF, DOCX, etc.)
   - **Entity Recognition**: Identifies key terms, definitions, and concepts
   - **Ambiguity Detection**: Flags unclear or contradictory clauses

2. **Enhancement Agent**
   - **Analysis**: Examines standard text for improvement opportunities
   - **Proposal Generation**: Creates enhancement suggestions
   - **Rationale Development**: Provides detailed justifications for changes
   - **Context Integration**: Incorporates regulatory and industry context

3. **Validation Agent**
   - **Shariah Compliance**: Validates against Islamic finance principles
   - **Financial Analysis**: Applies advanced financial models
   - **Risk Assessment**: Evaluates potential risks and issues
   - **Scoring**: Assigns compliance scores and recommendations

### Specialized Validators

1. **ShariahContractAnalyzer**
   - Comprehensive contract analysis
   - Multi-lingual support (English and Arabic)
   - Configurable compliance thresholds
   - Risk scoring and severity levels

2. **AdvancedFinancialRules**
   - Statistical models for financial analysis
   - Time-series analysis for risk assessment
   - Probability distributions for uncertainty modeling
   - Performance metrics for Shariah compliance

3. **KnowledgeGraphIntegrator**
   - Manages connections to Neo4j knowledge graph
   - Handles complex queries and relationships
   - Maintains data consistency and integrity

### System Integration

All components are connected through:

1. **Shared Database** - SQLite database storing standards, definitions, accounting treatments, transaction structures, ambiguities, enhancement proposals, validations, comments, votes, events, and audit logs.

2. **File Manager** - Handles document storage and sharing between components, including saving and retrieving standard documents, enhancement proposals, validation results, and event logs.

3. **Event Bus** - Enables asynchronous communication between agents, allowing for a decoupled architecture where components can publish and subscribe to events.

4. **System Integrator** - Orchestrates the flow of data and events between all components, ensuring seamless integration.

## 🛠️ Technical Specifications

### Backend Stack

- **Language**: Python 3.8+
- **Web Framework**: FastAPI with ASGI
- **Database**: 
  - Neo4j (Knowledge Graph)
  - PostgreSQL (Structured Data)
  - Redis (Caching & Pub/Sub)
- **Search**: Elasticsearch (Full-text search)
- **Message Broker**: RabbitMQ
- **Task Queue**: Celery
- **API Documentation**: OpenAPI 3.0 (Swagger/ReDoc)
- **Testing**: pytest, pytest-cov, pytest-asyncio

### Data Processing

- **Document Parsing**: PyMuPDF, python-docx, pdfplumber
- **NLP**: spaCy, NLTK, transformers
- **Data Validation**: Pydantic, jsonschema
- **Data Analysis**: pandas, NumPy, SciPy
- **Machine Learning**: scikit-learn, TensorFlow (optional)

### Frontend

- **Framework**: React.js with TypeScript
- **State Management**: Redux Toolkit
- **UI Components**: Material-UI
- **Data Visualization**: D3.js, Chart.js
- **Form Handling**: Formik with Yup validation
- **Testing**: Jest, React Testing Library

### DevOps

- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Documentation**: Sphinx, MkDocs

## 📚 Documentation

For detailed documentation, please visit our [documentation site](https://islamic-finance-standards.readthedocs.io/).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) to get started.

## 📧 Contact

For any questions or support, please contact [your-email@example.com](mailto:your-email@example.com).

## 🙏 Acknowledgments

- AAOIFI for their Islamic finance standards
- The open-source community for their valuable tools and libraries
- All contributors who have helped improve this project

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
