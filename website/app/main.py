import logging
from flask import Flask, request, redirect, url_for, render_template, Response
from authlib.integrations.requests_client import OAuth2Session
import json
from .db import create_tables, insert_repos
from .nd import normalize_data, deduplicate_data
import csv
import io
import os
from pathlib import Path
import dotenv
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

app = Flask(__name__)

deduplicated_data = None

# Set up the Github API endpoint URLs
authorize_url = "https://github.com/login/oauth/authorize"
access_token_url = "https://github.com/login/oauth/access_token"

# Set up the redirect URI
redirect_uri = "http://localhost:8000/callback"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"
dotenv.load_dotenv(ENV_FILE_PATH)

# Parameters for connecting to local PostgresQL server
params = {
    'host': os.environ.get('HOSTNAME'),
    'database' : os.environ.get('DATABASE'),
    'user' : os.environ.get('USER'),
    'password' : os.environ.get('PASSWORD')
}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def request_access_token(params):
    response = requests.post(access_token_url, params=params, headers={"Accept": "application/json"})
    response.raise_for_status()
    data = response.json()
    # Extract the access token from the response data
    return data.get("access_token")

@app.route("/")
def index():
    # Create an OAuth2Session() Object to connect to GitHub via the OAuth method
    oauth = OAuth2Session(os.environ.get('CLIENT_ID'), redirect_uri=redirect_uri)
    authorization_url, state = oauth.create_authorization_url(authorize_url, scope='repo')
    return redirect(authorization_url)

@app.route("/inputs")
def get_info():
    access_token = request.args.get('token')
    return render_template('input.html', access_token=access_token)

@app.route("/callback")
def callback():
    # Get the authorization code from the query parameters
    code = request.args.get("code")
    params = {
        "client_id": os.environ.get('CLIENT_ID'),
        "client_secret": os.environ.get('CLIENT_SECRET'),
        "code": code,
        "redirect_uri": redirect_uri
    }
    try:
        access_token = request_access_token(params)
        return redirect(url_for('get_info', token= access_token))
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving access token: {e}")
        return Response("Error retrieving access token", status=500)

@app.route("/download")
def download():
    # Create the CSV file, buffer and send it as a response object for the user to download
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['owner_id', 'owner_name', 'owner_email', 'repo_id', 'repo_name', 'repo_status', 'stars_count'])
    for row in deduplicated_data:
        writer.writerow([row['owner_id'], row['owner_name'], row['owner_email'], row['repo_id'], row['repo_name'], row['repo_status'], row['stars_count']])
    filename = 'output.csv'
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'text/csv'

    }

    return Response(
        csv_buffer.getvalue(),
        headers=headers,
        mimetype='text/csv'
    )


@app.route('/submit', methods=['POST'])
def submit():
    # Get the form data
    try:
        usernames = request.form.getlist('username[]')
        repositories = request.form.getlist('repository[]')
        access_token = request.form['access_token']
    except Exception as e:
        logging.error(f"Failed to parse form data: {e}")
        return "Failed to parse form data", 400
    
    # Process the repositories
    dataset = []
    for i, (user, repo) in enumerate(zip(usernames, repositories)):
        try:
            # Get user email
            response = requests.get(f'https://api.github.com/users/{user}', headers={'Authorization': 'Bearer ' + access_token})
            response.raise_for_status()
            email = response.json()['email']
            
            # Get repository info
            url = f"https://api.github.com/repos/{user}/{repo}"
            headers = {"Authorization": "Bearer " + access_token}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            repo = response.json()
            
            # Normalize and deduplicate data
            priv = 'Public' if not repo['private'] else 'Private'
            data = {
                "owner_id" : repo['owner']['id'],
                "owner_name" : repo['owner']['login'],
                "owner_email" : email,
                "repo_id" : repo['id'],
                "repo_name" : repo['name'],
                "repo_status" : priv,
                "stars_count": repo['stargazers_count']
            }
            dataset.append(normalize_data(json.dumps(data)))
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error while processing repository {i}: {e}")
            return f"Request error while processing repository {i}", 500
        except Exception as e:
            logging.error(f"Error while processing repository {i}: {e}")
            continue
    
    # Create tables and insert deduplicated data
    create_tables()
    global deduplicated_data
    deduplicated_data = deduplicate_data(dataset)
    try:
        insert_repos(deduplicated_data)
    except Exception as e:
        logging.error(f"Failed to insert deduplicated data: {e}")
        return "Failed to insert deduplicated data", 500
    
    # Redirect to download page
    return redirect(url_for('download'))
