import psycopg2
import time
import random
import os
import logging
import sys
import signal
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('data_producer')

# Get database connection parameters from environment variables
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'inventory')
DATA_TABLES = os.getenv('DATA_TABLES', 'customers,orders,products').split(',')
INSERT_INTERVAL_MIN = float(os.getenv('INSERT_INTERVAL_MIN', '1'))
INSERT_INTERVAL_MAX = float(os.getenv('INSERT_INTERVAL_MAX', '5'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '5'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '5'))

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    """Handle termination signals for graceful shutdown"""
    global running
    logger.info("Shutdown signal received, stopping data producer...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def retry_operation(operation_func, max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY):
    """Retry an operation with exponential backoff"""
    retries = 0
    while retries < max_retries:
        try:
            return operation_func()
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                logger.error(f"Operation failed after {max_retries} attempts: {e}")
                raise
            wait_time = retry_delay * (2 ** (retries - 1))
            logger.warning(f"Operation failed: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

def create_database():
    """Create the database if it doesn't exist"""
    logger.info(f"Checking if database {DB_NAME} exists...")
    
    # Connect to PostgreSQL server
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database="postgres",  # Connect to default database first
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True  # Required for creating database
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        
        if not exists:
            logger.info(f"Creating database {DB_NAME}...")
            cur.execute(f'CREATE DATABASE {DB_NAME}')
            logger.info(f"Database {DB_NAME} created successfully")
        else:
            logger.info(f"Database {DB_NAME} already exists")
        
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

def get_database_connection():
    """Get a connection to the database with retry logic"""
    def connect():
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    
    return retry_operation(connect)

def create_tables():
    """Create all required tables if they don't exist"""
    conn = get_database_connection()
    cur = conn.cursor()
    
    try:
        # Customers table
        if 'customers' in DATA_TABLES:
            logger.info("Creating customers table if it doesn't exist...")
            create_table_query = """
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cur.execute(create_table_query)
        
        # Products table
        if 'products' in DATA_TABLES:
            logger.info("Creating products table if it doesn't exist...")
            create_table_query = """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                category VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cur.execute(create_table_query)
        
        # Orders table
        if 'orders' in DATA_TABLES:
            logger.info("Creating orders table if it doesn't exist...")
            create_table_query = """
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'pending',
                total_amount DECIMAL(10, 2),
                CONSTRAINT fk_customer
                    FOREIGN KEY(customer_id)
                    REFERENCES customers(id)
                    ON DELETE SET NULL
            );
            """
            cur.execute(create_table_query)
            
            # Order items table
            logger.info("Creating order_items table if it doesn't exist...")
            create_table_query = """
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                CONSTRAINT fk_order
                    FOREIGN KEY(order_id)
                    REFERENCES orders(id)
                    ON DELETE CASCADE,
                CONSTRAINT fk_product
                    FOREIGN KEY(product_id)
                    REFERENCES products(id)
                    ON DELETE SET NULL
            );
            """
            cur.execute(create_table_query)
        
        conn.commit()
        logger.info("All tables created successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating tables: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def insert_customer() -> Optional[int]:
    """Insert a new customer record and return the ID"""
    first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Michael", 
                  "Emma", "David", "Olivia", "James", "Sophia", "William", "Ava"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                 "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    
    conn = get_database_connection()
    cur = conn.cursor()
    customer_id = None
    
    try:
        cur.execute(
            """
            INSERT INTO customers (first_name, last_name, email, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (first_name, last_name, email, datetime.now(), datetime.now())
        )
        customer_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Inserted new customer: {first_name} {last_name} (ID: {customer_id})")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting customer: {e}")
    finally:
        cur.close()
        conn.close()
        
    return customer_id

def insert_product() -> Optional[int]:
    """Insert a new product record and return the ID"""
    product_names = ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard", "Mouse",
                    "Headphones", "Speaker", "Camera", "Printer", "Router", "External Drive"]
    categories = ["Electronics", "Computers", "Accessories", "Audio", "Photography", "Networking"]
    
    name = random.choice(product_names)
    description = f"A high-quality {name.lower()} for everyday use"
    price = round(random.uniform(50, 1500), 2)
    category = random.choice(categories)
    
    conn = get_database_connection()
    cur = conn.cursor()
    product_id = None
    
    try:
        cur.execute(
            """
            INSERT INTO products (name, description, price, category, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (name, description, price, category, datetime.now(), datetime.now())
        )
        product_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Inserted new product: {name} (ID: {product_id})")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting product: {e}")
    finally:
        cur.close()
        conn.close()
        
    return product_id

def insert_order(customer_id: int, product_ids: List[int]) -> Optional[int]:
    """Insert a new order with order items"""
    if not product_ids:
        logger.warning("No products available for order")
        return None
    
    conn = get_database_connection()
    cur = conn.cursor()
    order_id = None
    
    try:
        # Get product prices
        products_info = {}
        for product_id in product_ids:
            cur.execute("SELECT price FROM products WHERE id = %s", (product_id,))
            result = cur.fetchone()
            if result:
                products_info[product_id] = result[0]
        
        # Create order items
        order_items = []
        total_amount = 0
        for product_id in random.sample(product_ids, min(len(product_ids), random.randint(1, 3))):
            quantity = random.randint(1, 5)
            unit_price = products_info.get(product_id, 0)
            total_amount += quantity * unit_price
            order_items.append((product_id, quantity, unit_price))
        
        # Insert order
        cur.execute(
            """
            INSERT INTO orders (customer_id, order_date, status, total_amount) 
            VALUES (%s, %s, %s, %s) RETURNING id
            """,
            (customer_id, datetime.now(), "pending", total_amount)
        )
        order_id = cur.fetchone()[0]
        
        # Insert order items
        for product_id, quantity, unit_price in order_items:
            cur.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price) 
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, product_id, quantity, unit_price)
            )
        
        conn.commit()
        logger.info(f"Inserted new order (ID: {order_id}) for customer {customer_id} with {len(order_items)} items")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting order: {e}")
        order_id = None
    finally:
        cur.close()
        conn.close()
        
    return order_id

def get_existing_ids(table: str) -> List[int]:
    """Get list of existing IDs from a table"""
    conn = get_database_connection()
    cur = conn.cursor()
    ids = []
    
    try:
        cur.execute(f"SELECT id FROM {table}")
        ids = [row[0] for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"Error getting IDs from {table}: {e}")
    finally:
        cur.close()
        conn.close()
        
    return ids

def main():
    try:
        logger.info("Starting data producer...")
        
        # Create database if it doesn't exist
        retry_operation(create_database)

        # Create tables if they don't exist
        retry_operation(create_tables)
        
        # Initial data generation for products if needed
        if 'products' in DATA_TABLES:
            product_ids = get_existing_ids('products')
            if not product_ids:
                logger.info("Generating initial product data...")
                for _ in range(10):  # Create some initial products
                    insert_product()
        
        # Main data generation loop
        while running:
            try:
                # Insert customer data
                if 'customers' in DATA_TABLES:
                    customer_id = insert_customer()
                
                    # Insert order data if both customers and orders are enabled
                    if customer_id and 'orders' in DATA_TABLES and 'products' in DATA_TABLES:
                        product_ids = get_existing_ids('products')
                        if product_ids:
                            insert_order(customer_id, product_ids)
                
                # Insert product data occasionally
                if 'products' in DATA_TABLES and random.random() < 0.2:  # 20% chance
                    insert_product()
                
                # Sleep for a random interval
                time.sleep(random.uniform(INSERT_INTERVAL_MIN, INSERT_INTERVAL_MAX))
            except Exception as e:
                logger.error(f"Error in data generation loop: {e}")
                time.sleep(RETRY_DELAY)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    logger.info("Data producer stopped")

if __name__ == "__main__":
    # Wait for PostgreSQL to be ready
    logger.info(f"Waiting for PostgreSQL to be ready at {DB_HOST}:{DB_PORT}...")
    time.sleep(10)
    main()
