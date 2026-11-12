import sys, json, base64, time
sys.stdout.reconfigure(line_buffering=True)
ct_hex = "4d990f713daecefb2c4903086fe0fff719a639e6e3d8f8bf43e3b8ec0e5cf4466bc2ab9753c2d2e6760791a5df802e316c7f677cbc2adf6135f91b0ba68298ab37d076f68629e1ba1fca8ee3e64b148a"
iv_hex = "ea5130a66a4e3d81a66fdc5a83d956f5"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]

def query(fp, tgt):
    payload = bytes(fp) + bytes(tgt)
    s = base64.b64encode(payload).decode()
    print(json.dumps({"q": s}, separators=(",", ":")), flush=True)
    line = sys.stdin.readline()
    if not line:
        print("EOF_ON_QUERY", file=sys.stderr, flush=True)
        raise RuntimeError("EOF from oracle")
    return bool(json.loads(line).get("pad_ok"))

def recover(tgt):
    I = bytearray(16)
    F = bytearray(16)
    for pos in range(15, -1, -1):
        n = 16 - pos
        for j in range(pos+1, 16):
            F[j] = I[j] ^ n
        ok_found = False
        for g in range(256):
            F[pos] = g
            try:
                ok = query(F, tgt)
            except RuntimeError:
                raise
            if ok:
                if n == 1:
                    sv = F[14]
                    F[14] = sv ^ 1
                    ok2 = query(F, tgt)
                    F[14] = sv
                    if not ok2:
                        continue
                I[pos] = g ^ n
                ok_found = True
                break
        if not ok_found:
            raise RuntimeError(f"no guess pos {pos}")
    return bytes(I)

t0 = time.monotonic_ns()
pt = b""
for idx, tgt in enumerate(blocks):
    print(f"RECOVER block {idx}", file=sys.stderr, flush=True)
    Im = recover(tgt)
    P = bytes(a ^ b for a, b in zip(Im, prevs[idx]))
    pt += P
    print(f"BLOCK {idx} done: {P.hex()}", file=sys.stderr, flush=True)
t1 = time.monotonic_ns()
pl = pt[-1]
if 1 <= pl <= 16 and pt[-pl:] == bytes([pl])*pl:
    pt_out = pt[:-pl]
else:
    pt_out = pt
print(f"OPSPAN_NS:{t1-t0}", flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": pt_out.hex()}, separators=(",", ":")), flush=True)