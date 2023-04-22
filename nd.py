import json
import psycopg2
from config import config

UNIQUE_KEYS = ['repo_id']
params = config()
conn = psycopg2.connect(**params)

def normalize_data(data):
    normalized = {}
    data = json.loads(data)
    for key, value in data.items():
        # Standardize the key names
        if key == 'owner_id':
            key = 'owner_id'
        elif key == 'owner_name':
            key = 'owner_name'
        elif key == 'owner_email':
            key = 'owner_email'
        elif key == 'repo id':
            key = 'repo_id'
        elif key == 'rep_ name':
            key = 'repo_name'
        elif key == 'repo_status':
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

def deduplicate_data(data_list):
    unique_data = {}
    for data in data_list:
        # Create a unique key for each data point
        key_parts = [str(data[key]) for key in UNIQUE_KEYS]
        # Debugging statement to check for duplicate key parts
        if len(key_parts) != len(set(key_parts)):
            print('Duplicate key parts:', key_parts)
        key = '-'.join(key_parts)
        # Debugging statement to check for duplicate keys
        if key in unique_data:
            print('Duplicate key:', key)
        # Add the data to the unique_data dictionary
        if key not in unique_data:
            unique_data[key] = data
        # Debugging statement to check the length of unique_data
        print('Length of unique_data:', len(unique_data))
    # Debugging statement to check the length of the final list
    print('Length of final list:', len(list(unique_data.values())))
    return list(unique_data.values())
