import requests
import json
import webbrowser
import base64


def get_session():

    config = json.load(open('config/access.json'))

    scopes = ['user-library-read',
              'playlist-read-private',
              'user-library-modify',
              'playlist-modify-public',
              'user-read-recently-played',
              'user-top-read',
              'playlist-modify-public',
              'playlist-modify-private']

    params = {
        'client_id': str(config['Client ID']),
        'response_type': 'code',
        'redirect_uri': 'https://localhost/',
        'scope': ' '.join(scopes)
    }

    s = requests.session()

    authorize = s.get('https://accounts.spotify.com/authorize',
                      params=params,
                      allow_redirects=True)

    print(authorize.url)

    webbrowser.open(authorize.url)

    auth_url = input('Redirected URL: ...')

    payload = {
        'grant_type': 'authorization_code',
        'code': str(auth_url).split("?code=")[1].split("&")[0],
        'redirect_uri': 'https://localhost/'
    }

    auth_header = base64.b64encode(str(config['Client ID'] + ':' + config['Client Secret']).encode('ascii'))

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + auth_header.decode('ascii')
    }

    auth_req = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=payload)

    headers = {
        'Authorization': 'Bearer ' + auth_req.json()['access_token'],
        'Content-Type': 'application/json',
        'Retry-After': '60'
    }

    s = requests.Session()
    s.headers.update(headers)

    if s.get('https://accounts.spotify.com/api/v1/me').status_code == 200:
        print('connected')

    return s

