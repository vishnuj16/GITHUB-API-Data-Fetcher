import requests
import json
import psycopg2
from config import config
from db import connect
from db import create_tables
from db import insert_repos
from nd import normalize_and_deduplicate
from convcsv import writecsv
from app import web
from authlib.integrations.requests_client import OAuth2Session


# Set the client ID and client secret
client_id = 'a4c580cf13acaa49fbe8'
client_secret = '2068e661eb34a10b99870814c14ebe37974717f0'

# Define the authorization URL and callback URL
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'
redirect_uri = 'https://localhost:8000/callback'

# Create an OAuth2Session object with the client ID and client secret
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)

# Generate the authorization URL and ask the user to visit it in their browser
authorization_url, state = oauth.create_authorization_url(authorization_base_url)

print('Please go to %s and authorize access.' % authorization_url)

# After the user grants access, Github will redirect the user to the callback URL with a code parameter
authorization_response = input('Enter the full callback URL: ')

# Use the code to obtain an access token
token = oauth.fetch_token(token_url, authorization_response=authorization_response, client_secret=client_secret)


#Get details of required repos from client
repos = []

while True:
    temp = input("Enter The username  and repository of the repo you need(N/n if you want to stop)  : ").split(' ')
    if temp[0]=='n' or temp[0]=='N':
        break
    repos.append(temp)

print(repos)



# Use the access token to make requests to the Github API


dataset = []


for item in repos:
    
    user = item[0]
    reponame = item[1]
    
    response = requests.get('https://api.github.com/users/' + user, headers={'Authorization': 'Bearer ' + token['access_token']})
    # print(response.json())
    response = response.json()
    # print(response)
    email = response['email']

    # Set up the API endpoint URL
    url = "https://api.github.com/repos/" + user + "/" + reponame
    # print(url)

    # Set up the headers with the access token
    headers = {
        "Authorization": "Bearer " + token['access_token']
    }

    # Make the API request and retrieve the data
    response = requests.get(url, headers=headers)
    repo = response.json()
    # print(data)
    
    # for repo in data:
    #     print(repo)
    
    priv = repo['private']
    if priv=='False':
        priv = 'Private'
    else:
        priv = 'Public'
    
    temp = {
    "Owner ID" : repo['owner']['id'],
    "Owner Name" : repo['owner']['login'],
    "Owner Email" : email,
    "Repo ID" : repo['id'],
    "Repo Name" : repo['name'],
    "Status" : priv,
    "Stars Count": repo['stargazers_count']
}
    temp2 = json.dumps(temp)
    dataset.append(temp2)


for info in dataset:
    print(info)
    print("\n")


#connect()

nd_dataset = normalize_and_deduplicate(dataset)

create_tables()
for info in nd_dataset:
    json_info = json.dumps(info)
    insert_repos(json_info)


#converting to csv file
writecsv(dataset)

#open webapp
web()