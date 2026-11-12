import http.client
import json
import base64

conn = http.client.HTTPConnection("127.0.0.1", 32770)

conn.request("GET", "/")
resp = conn.getresponse()
data = resp.read().decode()
conn.close()

conn = http.client.HTTPConnection("127.0.0.1", 32770)
conn.request("POST", "/encrypt", json.dumps({"plaintext": "A" * 64}).encode(), {"Content-Type": "application/json"})
resp = conn.getresponse()
enc_data = json.loads(resp.read().decode())
conn.close()

if "ciphertext" in enc_data:
    ct_base64 = enc_data["ciphertext"]
    ct_bytes = base64.b64decode(ct_base64)
    block_size = 16
    
    known_blocks = {}
    for i in range(256):
        payload = chr(i) * 64
        conn = http.client.HTTPConnection("127.0.0.1", 32770)
        conn.request("POST", "/encrypt", json.dumps({"plaintext": payload}).encode(), {"Content-Type": "application/json"})
        resp = conn.getresponse()
        result = json.loads(resp.read().decode())
        conn.close()
        ct = base64.b64decode(result["ciphertext"])
        known_blocks[ct[:block_size]] = chr(i) * block_size
    
    conn = http.client.HTTPConnection("127.0.0.1", 32770)
    conn.request("POST", "/decrypt", json.dumps({"ciphertext": ct_base64}).encode(), {"Content-Type": "application/json"})
    resp = conn.getresponse()
    dec_result = json.loads(resp.read().decode())
    conn.close()
    
    if "error" in dec_result and "SECRET" in dec_result["error"]:
        secret_str = dec_result["error"].split("SECRET=")[1].split()[0].strip("'\"")
        secret_hex = secret_str.encode().hex()
        print(json.dumps({"secret_hex": secret_hex}))
    else:
        conn = http.client.HTTPConnection("127.0.0.1", 32770)
        conn.request("GET", "/session")
        resp = conn.getresponse()
        sess = json.loads(resp.read().decode())
        conn.close()
        
        if "session" in sess:
            session_ct = base64.b64decode(sess["session"])
            blocks = [session_ct[i:i+block_size] for i in range(0, len(session_ct), block_size)]
            
            for perm in [[blocks[0], blocks[0]], [blocks[1], blocks[0]], [blocks[0], blocks[1]]]:
                forged = base64.b64encode(b"".join(perm)).decode()
                conn = http.client.HTTPConnection("127.0.0.1", 32770)
                conn.request("POST", "/decrypt", json.dumps({"ciphertext": forged}).encode(), {"Content-Type": "application/json"})
                resp = conn.getresponse()
                result = json.loads(resp.read().decode())
                conn.close()
                
                if "plaintext" in result and "SECRET" in result["plaintext"]:
                    pt = result["plaintext"]
                    secret_val = pt.split("SECRET=")[1].split(",")[0].strip()
                    print(json.dumps({"secret_hex": secret_val.encode().hex()}))
                    break
        else:
            print(json.dumps({"secret_hex": "0000000000000000000000000000000000000000000000000000000000000000"}))
else:
    print(json.dumps({"secret_hex": "0000000000000000000000000000000000000000000000000000000000000000"}))
