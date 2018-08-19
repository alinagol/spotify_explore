import login
import time
import json
import pandas as pd


# Login
s = login.get_session()

# My account
me = s.get('https://api.spotify.com/v1/me').json()

# Get recently played tracks
today = int(time.time())
after = today - 7*24*60

recent_tracks = s.get('https://api.spotify.com/v1/me/player/recently-played', params={'after': after, 'limit': 50}).json()

recent_tracks_ids = []

for item in recent_tracks['items']:
    recent_tracks_ids.append(item['track']['id'])

# Get attributes of the recently played tracks
recent_tracks_attributes = []

for track in recent_tracks_ids:

    try:

        tr = s.get('https://api.spotify.com/v1/audio-features/%s' % (track))

        if tr.status_code == 200:
            recent_tracks_attributes.append(tr.json())
        elif tr.status_code == 429:
            print('Sleeping...')
            time.sleep(30)
            tr = s.get('https://api.spotify.com/v1/audio-features/%s' % (track))
            recent_tracks_attributes.append(tr.json())
    except Exception as ex:
        print(ex)

df = pd.DataFrame(recent_tracks_attributes)

# Get recommendation based on attributes of the recent tracks
recommendations_parameters = {
    'limit': 25,
    'market': 'NL',
    'seed_tracks': recent_tracks_ids,
    'target_acousticness': df['acousticness'].describe()['50%'],
    'target_danceability': df['danceability'].describe()['50%'],
    'target_energy': df['energy'].describe()['50%'],
    'target_instrumentalness': df['instrumentalness'].describe()['50%'],
    'target_key': int(df['key'].describe()['50%']),
    'target_liveness': df['liveness'].describe()['50%'],
    'target_loudness': df['loudness'].describe()['50%'],
    'target_mode': int(df['mode'].describe()['50%']),
    'target_speechiness': df['speechiness'].describe()['50%'],
    'target_time_signature': int(df['time_signature'].describe()['50%']),
    'target_valence': df['valence'].describe()['50%'],
    'max_popularity': 50
}

recommendations = s.get('https://api.spotify.com/v1/recommendations', params=recommendations_parameters).json()

recommendations_uris = []

for r in recommendations['tracks']:
    recommendations_uris.append(r['uri'])

# Create a new playlist
playlist = {
  "name": "Smart Playlist %s" % time.strftime('%d-%m-%y'),
  "public": "true"
}

playlist = s.post('https://api.spotify.com/v1/users/%s/playlists' % me['id'], data=json.dumps(playlist)).json()

add_tracks = s.post('https://api.spotify.com/v1/playlists/%s/tracks' % playlist['id'],
                    data=json.dumps({'uris': recommendations_uris}))
