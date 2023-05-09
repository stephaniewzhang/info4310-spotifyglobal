import requests
import json
from os import environ

client_id = environ.get("CLIENT_ID")
client_secret = environ.get("CLIENT_SECRET")

AUTH_URL = 'https://accounts.spotify.com/api/token'

auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'

# load the json 
with open("./static/viral_50.json", "r") as file:
    data = json.load(file)

for key in data: 
    track_url = data[key]["url"]
    index = track_url.rfind("/") + 1
    track_id = track_url[index:]
    # r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)
    # r_json = r.json()
    # data[key]["danceability"] = r_json["danceability"]
    # data[key]["energy"] = r_json["energy"]
    # data[key]["acousticness"] = r_json["acousticness"]
    # data[key]["instrumentalness"] = r_json["instrumentalness"]
    # data[key]["valence"] = r_json["valence"]

    rp = requests.get(BASE_URL + "tracks/" + track_id, headers=headers)
    print(rp.headers)
    # rp_json = rp.json()
    data[key]["popularity"] = rp_json["popularity"] / 100
    # data[key]["popularity"] = 0.5 # todo: re-run script after retry time
    print(data[key])


json_data = json.dumps(data)

with open("./static/viral_50_with_features.json", "w") as file: 
    file.write(json_data)