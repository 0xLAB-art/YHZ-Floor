import base64

with open('almostxor.py','rb') as f:
    src = base64.b64decode(f.read()).decode()
exec(src)

with open('ciphertext','rb') as f:
    ct = base64.b64decode(f.read()).decode().strip()

for n in range(1,8):
    vals = get_vals(int(ct,16), n)
    for k in range(256):
        km = get_vals(k,n)
        ok = True
        for i in range(0,len(vals),len(km)):
            chunk = vals[i:i+len(km)]
            if len(chunk) < len(km):
                chunk += [0]*(len(km)-len(chunk))
            for j in range(len(km)):
                if (chunk[j] ^ km[j]) != km[j]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            print(n,k)
