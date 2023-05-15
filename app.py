from flask import *
from whitenoise import WhiteNoise
from os import environ
import random
import requests
import string
import urllib

client_id = environ.get("CLIENT_ID")
client_secret = environ.get("CLIENT_SECRET")
redirect_uri = environ.get("REDIRECT_URI")

app = Flask(__name__, template_folder="static/")
app.wsgi_app = WhiteNoise(app.wsgi_app, 
                          root='static/', 
                          prefix='', 
                          index_file='index.htm', 
                          autorefresh=True)


@app.route('/login') 
def login():
    state = random.choices(string.ascii_lowercase)
    scope = 'user-read-private user-read-email user-top-read'

    params_dict = {
        "response_type": "code", 
        "client_id": client_id, 
        "scope": scope, 
        "redirect_uri": redirect_uri, 
        "code_challenge_method": 'S256',
        "state": state
    }
    params = urllib.parse.urlencode(params_dict)

    redirect_url = "https://accounts.spotify.com/authorize" + ("?" + params if params else "")
    return redirect(redirect_url)

@app.route('/callback') 
def callback():
    access_token=""
    args = request.args
    code = args.getlist('code')[0]
    state = args.getlist('state')[0]  
    data = []

    # If authorization was successful
    if state:
        # Request access token
        data = {
            "code": code, 
            "redirect_uri": redirect_uri,
            "grant_type": 'authorization_code',
            "client_id": client_id,
            "code_verifier": state,
            "client_secret": client_secret
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post("https://accounts.spotify.com/api/token",data=data, headers=headers)

        if response.status_code == 200:
            res = response.json()
            access_token = res["access_token"]
            refresh_token = res["refresh_token"]

            # Get user's top 50 tracks in last 4 weeks
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            } 
            print("bearer", access_token)
            params = {
                "time_range": "short_term",
                "limit": 5, # todo - change back to 50 before submission
                "offset": 0
            }

            query_params = urllib.parse.urlencode(params)
            url = "https://api.spotify.com/v1/me/top/tracks?" + query_params
            track_data = []
            user_data = []
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                tracks = response.json()["items"]
                track_data = []
                for track in tracks: 
                    artist_data_response = requests.get(track["artists"][0]["href"], headers=headers)
                    artist_data = artist_data_response.json()
                    data = {
                        "id": track["id"], 
                        "name": track["name"],
                        "url": track["external_urls"]["spotify"],
                        "popularity": track["popularity"],
                        "image_url": track["album"]["images"][0]["url"], 
                        "artist": track["artists"][0]["name"],
                        "genres": artist_data["genres"],
                        "artist_url": artist_data["images"][0]["url"]
                    }
                    track_data.append(data)
                    
            user_url = "https://api.spotify.com/v1/me"
            user_response = requests.get(user_url, headers=headers)
            if user_response.status_code == 200: 
                user_data = user_response.json()["display_name"]

            data = {
                "track_data": track_data,
                "user_data": user_data
            }
            print("user data", user_data)

    return render_template("index.htm", data=data, access_token=access_token)

if __name__ == "__main__":
    app.run(threaded=True, port=5000)