from flask import Flask, render_template, session, abort, redirect, request, flash
import json
import time

import os
import pathlib

from flask_sqlalchemy import SQLAlchemy
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from dotenv import load_dotenv, find_dotenv
from . import my_db, pb
import sys
from functools import wraps

load_dotenv("/var/www/FlaskApp/FlaskApp/.env")

db = my_db.db

# codespecialist.com https://www.youtube.com/watch?v=FKgJEfrhU1E

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")
print(os.getenv("SQL_ALCHEMY_DATABASE_URI"))
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQL_ALCHEMY_DATABASE_URI")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, ".client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file = client_secrets_file,
    scopes = [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri = "https://sd3b25.online/callback"
)

alive = 0
data = {}


def login_is_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function(*args, **kwargs)
    return wrapper

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response = request.url)
    
    #if not session["state"] == request.args["state"]:
    #    abort(500)
        
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    
    id_info = id_token.verify_oauth2_token( id_token = credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID)
    
    session["google_id"] = id_info.get("sub")
    print(session["google_id"])
    session["name"] = id_info.get("name")
    print(session["name"])
    return redirect("/protected_area")

@app.route("/logout")
def logout():
    my_db.user_logout(session['google_id'])
    session.clear() 
    return redirect("/")

@app.route("/protected_area")
@login_is_required
def protected_area():
    print(session['name'])
    print(session['google_id'])
    my_db.add_user_and_login(session['name'], session['google_id'])
    is_admin = my_db.is_admin(session['google_id'])
    return render_template("protected_area.html", is_admin=is_admin, online_users=my_db.get_all_logged_in_users())

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/keep_alive")
def keep_alive():
    global alive, data
    alive += 1
    keep_alive_count = str(alive)
    data["keep_alive"] = keep_alive_count
    parsed_json = json.dumps(data)
    return str(parsed_json)


@app.route('/grant-<user_id>-<read>-<write>', methods=["POST"])
@login_is_required
def grant_access(user_id, read, write):
    is_admin = my_db.is_admin(session['google_id'])
    if is_admin:
        print(f"Admin granting {user_id}-{read}-{write}")
        my_db.add_user_permission(user_id, read, write)
        if read == "true" and write == "true":
            token = pb.grant_read_and_write_access(user_id)
            pb.parse_token(token)
            my_db.add_token(user_id, token)
            access_response={'token':token, 'cipher_key':pb.cipher_key, 'uuid':user_id}
            return json.dumps(access_response)
            
    

if __name__ == "__main__":
    app.run()
