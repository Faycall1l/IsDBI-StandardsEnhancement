#!/bin/bash
# Startup script for Islamic Finance Standards Enhancement System

# Set environment variables
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password123"
export GEMINI_API_KEY="AIzaSyC_P-2Dl1fo_gvD2EM43tRCOWv6aS-u5c4"
export USE_NEO4J="true"
export USE_KAFKA="true"  # Using Kafka for event streaming
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
export USE_GEMINI="true"
export USE_FABRIC="false"
export FLASK_SECRET_KEY="development-secret-key-change-in-production"
export FLASK_ENV="development"
export FLASK_DEBUG="1"

# Create necessary directories
mkdir -p audit_logs

# Check if Neo4j is running
echo "Checking if Neo4j is running..."
if nc -z localhost 7687 &>/dev/null; then
    echo "Neo4j is running."
else
    echo "Neo4j is not running. Starting Neo4j container..."
    docker run \
        --name neo4j-islamic-finance \
        -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/password123 \
        -v $HOME/neo4j/data:/data \
        -v $HOME/neo4j/logs:/logs \
        -v $HOME/neo4j/import:/var/lib/neo4j/import \
        -v $HOME/neo4j/plugins:/plugins \
        --restart always \
        -d neo4j:4.4
    
    # Wait for Neo4j to start
    echo "Waiting for Neo4j to start..."
    sleep 10
fi

# Set Python path and start the application
echo "Starting Islamic Finance Standards Enhancement System..."
PYTHONPATH=/Users/faycalamrouche/Desktop/IsDBI .venv/bin/python IslamicFinanceStandardsAI/frontend/app.py
