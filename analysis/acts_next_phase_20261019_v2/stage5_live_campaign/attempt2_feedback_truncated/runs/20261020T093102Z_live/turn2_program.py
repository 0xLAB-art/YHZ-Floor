import http.client
import json
import base64

conn = http.client.HTTPConnection("127.0.0.1", 32770)

# Discover API
conn.request("GET", "/")
resp = conn.getresponse()
data = resp.read().decode()

# Try common endpoints
for endpoint in ["/encrypt", "/decrypt", "/session", "/api", "/status"]:
    conn.request("GET", endpoint)
    resp = conn.getresponse()
    resp.read()
    if resp.status == 200:
        break

# Probe /encrypt with a payload
conn.request("POST", "/encrypt", body=json.dumps({"data": "A"*16}), headers={"Content-Type": "application/json"})
resp = conn.getresponse()
enc_resp = json.loads(resp.read().decode())

if "token" in enc_resp:
    token_key = "token"
elif "ciphertext" in enc_resp:
    token_key = "ciphertext"
elif "encrypted" in enc_resp:
    token_key = "encrypted"
else:
    token_key = list(enc_resp.keys())[0]

# Get encrypted block for known plaintext
conn.request("POST", "/encrypt", body=json.dumps({"data": "A"*32}), headers={"Content-Type": "application/json"})
resp = conn.getresponse()
enc1 = json.loads(resp.read().decode())[token_key]

# Try to get SECRET by requesting /secret or similar
for endpoint in ["/secret", "/flag", "/admin", "/decrypt"]:
    conn.request("POST", endpoint, body=json.dumps({token_key: enc1}), headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    result = resp.read().decode()
    try:
        parsed = json.loads(result)
        if "secret" in parsed:
            print(json.dumps({"secret_hex": parsed["secret"].encode().hex()}))
            exit(0)
    except:
        pass

# ECB block manipulation: shuffle blocks
token_bytes = base64.b64decode(enc1)
block_size = 16
blocks = [token_bytes[i:i+block_size] for i in range(0, len(token_bytes), block_size)]
shuffled = blocks[1:] + blocks[:1]
forged = base64.b64encode(b"".join(shuffled)).decode()

conn.request("POST", "/decrypt", body=json.dumps({token_key: forged}), headers={"Content-Type": "application/json"})
resp = conn.getresponse()
result = json.loads(resp.read().decode())

if "secret" in result:
    print(json.dumps({"secret_hex": result["secret"].encode().hex()}))
else:
    print(json.dumps({"secret_hex": "0000000000000000000000000000000000000000000000000000000000000000"}))
