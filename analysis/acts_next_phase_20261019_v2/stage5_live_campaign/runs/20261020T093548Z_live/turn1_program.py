import http.client
import json
import base64

HOST = "127.0.0.1"
PORT = 32773

def request(method, path, body=None):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/json"} if body else {}
    conn.request(method, path, body, headers)
    resp = conn.getresponse()
    data = resp.read().decode()
    conn.close()
    return resp.status, data

# Probe the service
print("=== Probing service ===")
status, data = request("GET", "/")
print(f"GET / -> {status}: {data}")

status, data = request("GET", "/encrypt")
print(f"GET /encrypt -> {status}: {data}")

status, data = request("POST", "/encrypt", json.dumps({"plaintext": "test"}))
print(f"POST /encrypt test -> {status}: {data}")

# Try to find session endpoints
status, data = request("GET", "/session")
print(f"GET /session -> {status}: {data}")

status, data = request("POST", "/session", json.dumps({}))
print(f"POST /session -> {status}: {data}")

# Try creating a session with known data
test_data = {"user": "admin", "role": "user"}
status, data = request("POST", "/session", json.dumps(test_data))
print(f"POST /session with data -> {status}: {data}")

if status == 200:
    resp_json = json.loads(data)
    if "token" in resp_json:
        token = resp_json["token"]
        print(f"Got token: {token}")
        
        # Decode the token to see block structure
        token_bytes = base64.b64decode(token)
        print(f"Token length: {len(token_bytes)} bytes")
        print(f"Token hex: {token_bytes.hex()}")
        
        # Try different session data to understand structure
        for payload in [
            {"user": "A"*16, "role": "user"},
            {"user": "B"*16, "role": "user"},
            {"user": "admin", "role": "admin"},
        ]:
            status, data = request("POST", "/session", json.dumps(payload))
            if status == 200:
                tok = json.loads(data).get("token")
                if tok:
                    print(f"Payload {payload} -> token: {base64.b64decode(tok).hex()}")

# Try to verify/use a token
status, data = request("POST", "/verify", json.dumps({"token": token}))
print(f"POST /verify -> {status}: {data}")

# Look for secret endpoint
status, data = request("GET", "/secret")
print(f"GET /secret -> {status}: {data}")

status, data = request("POST", "/secret", json.dumps({"token": token}))
print(f"POST /secret with token -> {status}: {data}")
