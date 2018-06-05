from pymongo import MongoClient
import json
import requests
import json
import base64
import time


# MongoDB

cfg = json.load(open('config/mongo.json'))

db = 'mongodb://{host}:{port}'.format(**cfg['local'])  # local DB
with MongoClient(db) as client:
    tracksDB = client[cfg['local']['database']]['tracks']
    artistsDB = client[cfg['local']['database']]['artists']

# Spotify

config = json.load(open('config/access.json'))
auth_header = base64.b64encode(str(config['Client ID'] + ':' + config['Client Secret']).encode('ascii'))
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic '+ auth_header.decode('ascii')
}

payload = {'grant_type': 'client_credentials'}
auth_req = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=payload)

headers = {
    'Authorization': 'Bearer ' + auth_req.json()['access_token'],
    'Content-Type': 'application/json',
    'Retry-After': '60'
}

s = requests.Session()
s.headers.update(headers)

# Insert

artist_ids = list(set(json.load(open('artists.json'))))

payload = {'country': 'NL'}

tracks = []

for artist in artist_ids:
    tracks.extend(s.get('https://api.spotify.com/v1/artists/%s/top-tracks' % artist,
                        headers=headers, params=payload).json()['tracks'])

for track in tracks:
    tr = s.get('https://api.spotify.com/v1/audio-features/%s' % (track['id']), headers=headers)
    if tr.status_code == 200:
        tr = tr.json()
        tr.update({'name': track['name'], 'popularity': track['popularity'], 'artist': track['artists'][0]['name']})
        tracksDB.insert(tr)
    elif tr.status_code == 429:
        print('Sleeping...')
        time.sleep(30)
        tr = s.get('https://api.spotify.com/v1/audio-features/%s' % (track['id']), headers=headers).json()
        tr.update({'name': track['name'], 'popularity': track['popularity'], 'artist': track['artists'][0]['name']})
        tracksDB.insert(tr)
    else:
        print(tr.status_code)
