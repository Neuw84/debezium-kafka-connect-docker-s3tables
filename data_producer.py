import psycopg2
import time
from random import choice
import random
import os

# Get database connection parameters from environment variables
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'inventory')


def get_database_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def insert_customer():
    first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
    
    first_name = choice(first_names)
    last_name = choice(last_names)
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    
    conn = get_database_connection()
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO customers (first_name, last_name, email) VALUES (%s, %s, %s)",
        (first_name, last_name, email)
    )
    
    conn.commit()
    cur.close()
    conn.close()

def create_customers_table():
    conn = get_database_connection()
    cur = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS customers (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        last_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL
    );
    """
    
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

def main():
    try:
        # Create the customers table if it doesn't exist
        create_customers_table()
        print("Initialized customers table")
        
        while True:
            try:
                insert_customer()
                print("Inserted new customer")
                time.sleep(random.uniform(1, 5))
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        exit(1)

if __name__ == "__main__":
    # Wait for PostgreSQL to be ready
    time.sleep(10)
    main()
