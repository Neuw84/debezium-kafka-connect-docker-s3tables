#!/bin/bash

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Register the Postgres source connector
echo "Registering Postgres connector..."
curl -X POST -H "Content-Type: application/json" --data @connectors/register-postgres-connector.json http://localhost:8083/connectors

# Register the Iceberg sink connector
 
echo "Registering Iceberg sink connector..."
curl -X POST -H "Content-Type: application/json" --data @connectors/register-iceberg-sink.json http://localhost:8084/connectors

