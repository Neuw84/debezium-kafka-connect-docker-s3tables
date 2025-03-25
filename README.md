# Debezium Streaming Solution

This project demonstrates a streaming solution using Debezium with PostgreSQL, Kafka, on both local development mode using ```Docker```
 and AWS infrastructure(ongoing...).

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

### Components Overview 
- PostgreSQL: Source database.
- Debezium: Change Data Capture (CDC) tool deployed on top of Kafka Connect.
- Apache Kafka: Message broker.
- Iceberg Kafka Connect Sink: Kafka Connect Sink that uses Iceberg format.
- Minio: high-performance, S3-compatible object storage system.


## Architecture

See [architecture.md](architecture.md) for a detailed architecture diagram and component description.





