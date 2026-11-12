import http.client
import json
import sys

host = "127.0.0.1"
port = 32773

def request(method, path, body=None, headers=None):
    conn = http.client.HTTPConnection(host, port)
    if headers is None:
        headers = {}
    if body is not None and "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"
    conn.request(method, path, body, headers)
    resp = conn.getresponse()
    data = resp.read().decode()
    conn.close()
    return resp.status, data

print("=== Discovery phase ===")
status, data = request("GET", "/session")
print(f"GET /session -> {status}: {data}")
session = json.loads(data)
token = session["token_hex"]
token_bytes = bytes.fromhex(token)
print(f"Token: {token} ({len(token_bytes)} bytes)")

status, data = request("GET", "/")
print(f"GET / -> {status}: {data}")

status, data = request("POST", "/", json.dumps({"token": token}))
print(f"POST / with token -> {status}: {data}")

status, data = request("POST", "/session", json.dumps({"token": token}))
print(f"POST /session with token -> {status}: {data}")

status, data = request("POST", "/session", json.dumps({"token": token, "action": "read"}))
print(f"POST /session action=read -> {status}: {data}")

status, data = request("GET", "/session/" + token)
print(f"GET /session/{token[:16]}... -> {status}: {data}")

status, data = request("POST", "/verify", json.dumps({"token": token}))
print(f"POST /verify -> {status}: {data}")

status, data = request("POST", "/action", json.dumps({"token": token, "action": "read"}))
print(f"POST /action -> {status}: {data}")

status, data = request("POST", "/read", json.dumps({"token": token}))
print(f"POST /read -> {status}: {data}")

print("\n=== Block manipulation ===")
block1 = token_bytes[:16]
block2 = token_bytes[16:32]
swapped = block2 + block1
swapped_hex = swapped.hex()
print(f"Swapped token: {swapped_hex}")

status, data = request("POST", "/read", json.dumps({"token": swapped_hex}))
print(f"POST /read swapped -> {status}: {data}")

status, data = request("POST", "/action", json.dumps({"token": swapped_hex, "action": "read"}))
print(f"POST /action swapped -> {status}: {data}")

duplicated = block1 + block1
dup_hex = duplicated.hex()
status, data = request("POST", "/read", json.dumps({"token": dup_hex}))
print(f"POST /read duplicated -> {status}: {data}")
