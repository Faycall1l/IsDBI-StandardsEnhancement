#!/bin/bash
# Environment variables for Islamic Finance Standards Enhancement System

# API Keys
export GEMINI_API_KEY="your-gemini-api-key"
export SERP_API_KEY="your-serp-api-key"

# Flask configuration
export FLASK_SECRET_KEY="development-secret-key-change-in-production"
export FLASK_ENV="development"
export FLASK_DEBUG="1"

# Neo4j configuration
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"

# Kafka configuration
export USE_KAFKA="false"
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
export KAFKA_GROUP_ID="islamic_finance_standards"

# Blockchain configuration
export USE_FABRIC="false"
export FABRIC_NETWORK_PROFILE="blockchain/connection-profile.json"
export FABRIC_CHANNEL_NAME="mychannel"
export FABRIC_CHAINCODE_NAME="auditlog"
export FABRIC_ORG_NAME="Org1"
export FABRIC_USER_NAME="Admin"

# Feature flags
export USE_GEMINI="true"
