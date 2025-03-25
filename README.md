# Debezium Streaming Solution

This project demonstrates a streaming solution using Debezium with PostgreSQL, Kafka, on both local development mode using ```Docker```
 and AWS.

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


## AWS Deployment setup ( ongoing)
1. Prerequisites:
   - AWS CLI installed and configured
   - Necessary IAM permissions

2. CloudFormation Deployment:
   ```bash
   aws cloudformation create-stack \
       --stack-name debezium-stack \
       --template-body file://cloudformation.yaml \
       --capabilities CAPABILITY_IAM
   ```

3. Post-deployment:
   - Configure security groups
   - Set up Debezium connector in MSK Connect
   - Upload Python code to S3
   - Start Glue job

### Data Flow

1. Data changes in PostgreSQL trigger WAL events
2. Debezium captures changes and forwards to Kafka
3. Changes are streamed through MSK
4. Glue job processes the data
5. Results stored in S3 data lake

### Monitoring and Management

- Use CloudWatch for AWS service monitoring
- Docker logs for local environment
- MSK Connect dashboard for connector status
- Glue job logs for processing status


## Architecture

See [architecture.md](architecture.md) for a detailed architecture diagram and component description.

# License

This code is licensed under the Apache License. See the LICENSE file.





