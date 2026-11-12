import http.client
import json
import base64

host = "127.0.0.1"
port = 32773

def req(method, path, body=None):
    conn = http.client.HTTPConnection(host, port)
    headers = {"Content-Type": "application/json"} if body else {}
    conn.request(method, path, body=json.dumps(body) if body else None, headers=headers)
    resp = conn.getresponse()
    data = resp.read().decode()
    conn.close()
    return resp.status, data

# Discover endpoints
for path in ["/", "/api", "/session", "/encrypt", "/decrypt", "/login", "/auth"]:
    status, data = req("GET", path)
    if status != 404:
        print(f"GET {path} -> {status}: {data}")

for path in ["/session", "/encrypt", "/login", "/auth", "/register"]:
    status, data = req("POST", path, {})
    if status != 404:
        print(f"POST {path} -> {status}: {data}")

# Try to create a session and manipulate ECB blocks
status, data = req("POST", "/session", {"username": "A" * 16})
print(f"Session create: {status}, {data}")

if status == 200:
    resp = json.loads(data)
    token = resp.get("token") or resp.get("session")
    if token:
        token_bytes = base64.b64decode(token)
        print(f"Token length: {len(token_bytes)}")
        
        # Try different usernames to find block boundaries
        for length in [16, 32, 48]:
            s, d = req("POST", "/session", {"username": "A" * length})
            if s == 200:
                t = json.loads(d).get("token") or json.loads(d).get("session")
                print(f"Username length {length}: token blocks = {len(base64.b64decode(t)) // 16}")
        
        # Create admin token by block manipulation
        s1, d1 = req("POST", "/session", {"username": "A" * 16 + "admin"})
        if s1 == 200:
            t1 = base64.b64decode(json.loads(d1).get("token") or json.loads(d1).get("session"))
            forged = t1[:16] + t1[32:37]  # Take first block + admin block
            forged_token = base64.b64encode(forged).decode()
            
            # Try to use forged token
            status, data = req("GET", "/secret", headers={"Authorization": f"Bearer {forged_token}"})
            print(f"Secret attempt: {status}, {data}")
