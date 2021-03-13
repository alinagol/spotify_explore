import logging
import os

import pymongo
from flask import Flask, jsonify, redirect, render_template, request, url_for

log = logging.getLogger(__name__)

app = Flask(__name__)


mongo_uri = f'mongodb://{os.getenv("MONGODB_USERNAME")}:{os.getenv("MONGODB_PASSWORD")}@{os.getenv("MONGODB_HOSTNAME")}:27017'
with pymongo.MongoClient(mongo_uri) as client:
    db_tracks = client[os.getenv("MONGODB_DATABASE")]["tracks"]
    db_tracks_no_id = client[os.getenv("MONGODB_DATABASE")]["tracks_no_id"]


@app.route("/")
def home():
    n_tracks = db_tracks.count_documents()
    return render_template("home.html", count=n_tracks)
