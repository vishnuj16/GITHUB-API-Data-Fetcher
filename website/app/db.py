import psycopg2
import json
import os
from pathlib import Path
import dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"
dotenv.load_dotenv(ENV_FILE_PATH)


#Parameters for connecting to local PostgresQL server
params = {
    'host': os.environ.get('HOSTNAME'),
    'database' : os.environ.get('DATABASE'),
    'user' : os.environ.get('USER'),
    'password' : os.environ.get('PASSWORD')
}

def create_tables():
    command = """
        CREATE TABLE IF NOT EXISTS repos (
        owner_id SERIAL,
        owner_name TEXT,
        owner_email TEXT,
        repo_id bigint,
        repo_name TEXT,
        repo_status TEXT,
        stars_count INTEGER,
        PRIMARY KEY (repo_id)
    );
        """
    conn = None
    try:
        # read the connection parameters
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def insert_repos(data_list):
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        for data in data_list:
            print("insert into db data : ", data)
            data_str = json.dumps(data)
            cur.execute(f"INSERT INTO repos ({','.join(data.keys())}) VALUES ({','.join(['%s']*len(data))})", list(data.values()))
        # Commit the changes and close the cursor
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
