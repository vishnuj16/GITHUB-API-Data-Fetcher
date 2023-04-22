import json
import psycopg2

# Define the unique key fields
UNIQUE_KEYS = ['owner_id', 'repo_id']

# Define the PostgreSQL connection parameters
DB_HOST = 'localhost'
DB_NAME = 'mydatabase'
DB_USER = 'myuser'
DB_PASS = 'mypassword'

# Define the table name
TABLE_NAME = 'mytable'

# Connect to the PostgreSQL database
conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

# Define a function to normalize the JSON data
def normalize_data(data):
    normalized = {}
    for key, value in data.items():
        # Standardize the key names
        if key == 'owner id':
            key = 'owner_id'
        elif key == 'owner name':
            key = 'owner_name'
        elif key == 'owner email':
            key = 'owner_email'
        elif key == 'repo id':
            key = 'repo_id'
        elif key == 'repo name':
            key = 'repo_name'
        elif key == 'repo status':
            key = 'repo_status'
        elif key == 'stars_count':
            key = 'stars_count'
        # Standardize the values
        if value == 'null':
            value = None
        elif isinstance(value, str):
            value = value.strip()
        normalized[key] = value
    return normalized

# Define a function to deduplicate the data
def deduplicate_data(data_list):
    unique_data = {}
    for data in data_list:
        # Create a unique key for each data point
        key_parts = [data[key] for key in UNIQUE_KEYS]
        key = '-'.join(key_parts)
        # Add the data to the unique_data dictionary
        if key not in unique_data:
            unique_data[key] = data
    return list(unique_data.values())

# Define a function to load the data into the PostgreSQL database
def load_data(data_list):
    # Create a cursor and execute the INSERT statement for each data point
    cur = conn.cursor()
    for data in data_list:
        cur.execute(f"INSERT INTO {TABLE_NAME} ({','.join(data.keys())}) VALUES ({','.join(['%s']*len(data))})", list(data.values()))
    # Commit the changes and close the cursor
    conn.commit()
    cur.close()

# Define the JSON data
json_data = [
    {"owner id": "1", "owner name": "Alice", "owner email": "alice@example.com", "repo id": "1", "repo name": "MyRepo", "repo status": "active", "stars_count": "10"},
    {"owner id": "2", "owner name": "Bob", "owner email": "bob@example.com", "repo id": "2", "repo name": "AnotherRepo", "repo status": "inactive", "stars_count": "5"},
    {"owner id": "1", "owner name": "Alice", "owner email": "alice@example.com", "repo id": "1", "repo name": "MyRepo", "repo status": "active", "stars_count": "20"},
    {"owner id": "3", "owner name": "Charlie", "owner email": "charlie@example.com", "repo id": "3", "repo name": "ThirdRepo", "repo status": "active", "stars_count": "15"}
]

# Normalize the JSON data
normalized_data = [normalize_data(data) for data in json_data]

# Deduplicate the normalized data
deduplicated_data = deduplicate_data(normalized_data)

# Load the deduplicated data into the PostgreSQL database
load_data(deduplicated_data)

# Close the PostgreSQL connection
conn.close()
