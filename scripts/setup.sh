#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Function to check if a service is ready
check_service() {
  local service_name=$1
  local url=$2
  local max_attempts=$3
  local wait_seconds=$4
  
  echo "Checking if $service_name is ready..."
  
  for ((i=1; i<=$max_attempts; i++)); do
    if curl -s -f "$url" > /dev/null 2>&1; then
      echo "$service_name is ready!"
      return 0
    else
      echo "Waiting for $service_name to be ready... Attempt $i/$max_attempts"
      sleep $wait_seconds
    fi
  done
  
  echo "ERROR: $service_name is not ready after $max_attempts attempts"
  return 1
}

# Function to register a connector with error handling
register_connector() {
  local connector_name=$1
  local config_file=$2
  local url=$3
  local max_attempts=$4
  
  echo "Registering $connector_name..."
  
  for ((i=1; i<=$max_attempts; i++)); do
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" --data @"$config_file" "$url")
    
    if [[ "$response" == "201" || "$response" == "200" ]]; then
      echo "$connector_name registered successfully!"
      return 0
    else
      echo "Failed to register $connector_name. Status code: $response. Attempt $i/$max_attempts"
      sleep 5
    fi
  done
  
  echo "ERROR: Failed to register $connector_name after $max_attempts attempts"
  return 1
}

# Wait for Kafka Connect services to be ready
check_service "Debezium Connect" "http://localhost:8083/connectors" 12 5
check_service "Iceberg Connect" "http://localhost:8084/connectors" 12 5

# Register the Postgres source connector
register_connector "Postgres connector" "connectors/register-postgres-connector.json" "http://localhost:8083/connectors" 3

# Register the Iceberg sink connector
register_connector "Iceberg sink connector" "connectors/register-iceberg-sink.json" "http://localhost:8084/connectors" 3

echo "Setup completed successfully!"
