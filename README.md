# Debezium Streaming Solution

This project demonstrates a streaming solution using Debezium with PostgreSQL, Kafka, and AWS infrastructure.

## Local Development Setup

1. Start the containers:
```bash
docker-compose up -d
```

2. Wait for all services to be up and running

3. Run the setup script:
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This script will:
- Wait for all services to be ready
- Register the Postgres source connector
- Register the Iceberg sink connector

## Cleaning up Local Development

```bash
docker-compose down -v
```


## AWS Deployment

1. Deploy the CloudFormation template:
```bash
aws cloudformation create-stack --stack-name debezium-stack --template-body file://deploy.yaml
```

2. Once the stack is created, you'll need to:
   - Push the Debezium Connect image to ECR
   - Configure the security groups and networking
   - Set up the Debezium connector on ECS

## Architecture

See [architecture.md](architecture.md) for a detailed architecture diagram and component description.

### Components Overview
- PostgreSQL: Source database
- Debezium: Change Data Capture (CDC) tool
- Apache Kafka: Message broker
- AWS MSK: Managed Kafka service
- AWS RDS: Managed PostgreSQL database
- AWS ECS: Container orchestration for Debezium Connect
