# Debezium Streaming Solution

This project demonstrates a streaming solution using Debezium with PostgreSQL, Kafka, on both local development mode using ```Docker```
 and AWS.

 ## Features

- Real-time Change Data Capture (CDC) from PostgreSQL using Debezium
- Multi-table support (customers, products, orders, order_items)
- Streaming data to Apache Iceberg tables via Kafka Connect
- Interactive data analysis with Spark and Jupyter notebooks
- Robust error handling and logging
- Local development environment with Docker Compose
- AWS deployment with CloudFormation


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
- Check if all services are ready with proper health checks
- Register the Postgres source connector with Debezium
- Register the Iceberg sink connector
- Start the data producer

## Data Model

The project includes the following tables:

- **customers**: Customer information (first_name, last_name, email)
- **products**: Product catalog (name, description, price, category)
- **orders**: Customer orders (customer_id, order_date, status, total_amount)
- **order_items**: Order line items (order_id, product_id, quantity, unit_price)

## Cleaning up Local Development

```bash
docker-compose down -v
```

### Components Overview
- **PostgreSQL**: Source database with logical replication enabled
- **Debezium**: Change Data Capture (CDC) tool for streaming database changes
- **Apache Kafka**: Message broker for reliable data streaming
- **Apache Iceberg**: Table format for data lake storage
- **MinIO**: S3-compatible object storage (local development)
- **Spark**: Data processing engine for analytics
- **AWS MSK**: Managed Kafka service (AWS deployment)
- **AWS RDS**: Managed PostgreSQL database (AWS deployment)
- **AWS Glue**: Serverless data integration service (AWS deployment)

## Monitoring and Management

- **Kafka UI**: Available at http://localhost:8080 for monitoring Kafka topics and connectors
- **MinIO Console**: Available at http://localhost:9001 for exploring S3 storage
- **Jupyter Notebook**: Available at http://localhost:8888 for data analysis

## AWS Deployment setup

Use the CF template provided in ```infrastructure.yml``` file and follow the instructions of the Medium [blogpost](https://medium.com/@neuw84/using-debezium-and-kafka-connect-with-iceberg-part-ii-0c5ecea68c5e).

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

## Customization

You can customize the data generation by setting environment variables in the docker-compose.yml file:

- `DATA_TABLES`: Comma-separated list of tables to generate data for
- `INSERT_INTERVAL_MIN`: Minimum interval between inserts (seconds)
- `INSERT_INTERVAL_MAX`: Maximum interval between inserts (seconds)
- `MAX_RETRIES`: Maximum number of retries for database operations
- `RETRY_DELAY`: Delay between retries (seconds)


## Architecture

See [architecture.md](architecture.md) for a detailed architecture diagram and component description.

# License

This code is licensed under the Apache License. See the LICENSE file.





