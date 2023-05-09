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
    scope = 'user-top-read'

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
            params = {
                "time_range": "short_term",
                "limit": 50,
                "offset": 0
            }

            query_params = urllib.parse.urlencode(params)
            url = "https://api.spotify.com/v1/me/top/tracks?" + query_params
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                tracks = response.json()["items"]
                data = [{"id": track["id"], "name": track["name"], "url": track["external_urls"]["spotify"], "popularity": track["popularity"]} for track in tracks]
    return render_template("index.htm", data=data, access_token=access_token)

if __name__ == "__main__":
    app.run(threaded=True, port=5000)