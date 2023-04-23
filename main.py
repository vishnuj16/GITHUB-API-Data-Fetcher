from flask import Flask, request, redirect, url_for, render_template, Response
from authlib.integrations.requests_client import OAuth2Session
import json
from db import connect
from db import create_tables
from db import insert_repos
from nd import normalize_data, deduplicate_data
import csv
import io

import requests

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

deduplicated_data = None

# Set up the Github API endpoint URLs
authorize_url = "https://github.com/login/oauth/authorize"
access_token_url = "https://github.com/login/oauth/access_token"

# Set the client ID and client secret
client_id = '3b567f465ee4eb61c635'
client_secret = 'daff73b804991e71c343816228f8339fd15d9c98'

# Set up the redirect URI
redirect_uri = "http://localhost:8000/callback"

@app.route("/")
def index():
    
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)

    # Set up the authorization URL with the necessary parameters
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
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri
    }

    response = requests.post(access_token_url, params=params, headers={"Accept": "application/json"})
    data = response.json()

    # Extract the access token from the response data
    access_token = data.get("access_token")

    return redirect(url_for('get_info', token= access_token))

@app.route("/download")
def download():
    
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
    usernames = request.form.getlist('username[]')
    repositories = request.form.getlist('repository[]')
    access_token = request.form['access_token']

    repos = []
    for i in range(len(usernames)):
        temp = []
        temp.append(usernames[i])
        temp.append(repositories[i])
        repos.append(temp)
    
    print(repos)
    
    dataset = []
    for item in repos:
        
        user = item[0]
        reponame = item[1]
        
        response = requests.get('https://api.github.com/users/' + user, headers={'Authorization': 'Bearer ' + access_token})
        response = response.json()
        email = response['email']

        # Set up the API endpoint URL
        url = "https://api.github.com/repos/" + user + "/" + reponame
        headers = {
            "Authorization": "Bearer " + access_token
        }

        # Make the API request and retrieve the data
        response = requests.get(url, headers=headers)
        repo = response.json()
        
        priv = repo['private']
        if priv=='False':
            priv = 'Private'
        else:
            priv = 'Public'
        
        temp = {
        "owner_id" : repo['owner']['id'],
        "owner_name" : repo['owner']['login'],
        "owner_email" : email,
        "repo_id" : repo['id'],
        "repo_name" : repo['name'],
        "repo_status" : priv,
        "stars_count": repo['stargazers_count']
    }
        temp2 = json.dumps(temp)
        dataset.append(temp2)
    
    create_tables()


    # Normalize the JSON data
    normalized_data = [normalize_data(data) for data in dataset]

    # Deduplicate the normalized data
    global deduplicated_data
    deduplicated_data = deduplicate_data(normalized_data)
    insert_repos(deduplicated_data)

    return redirect(url_for('download'))

app.run(port=8000)
