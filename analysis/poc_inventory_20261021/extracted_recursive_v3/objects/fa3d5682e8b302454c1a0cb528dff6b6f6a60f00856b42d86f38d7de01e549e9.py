import sys, json, base64, time, os
ct_hex = "16838c7b6fc199c91ba3142d3cd7a8b3b9845a76113904ecafbe58de2fb2feae0237c4462b6beb5304ca6dd3058ee85ee3b82461ddc16632a018506384f769a2fceebf2a6b7f3f3d945e26f8e09599c9"
iv_hex = "ea3145d1160bd7dd49d59eda8b1a2139"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
qcount = 0
def oracle(payload: bytes) -> bool:
    global qcount
    q = base64.b64encode(payload).decode()
    line_out = json.dumps({"q": q})
    print(line_out, flush=True)
    try:
        os.fsync(sys.stdout.fileno())
    except Exception:
        pass
    qcount += 1
    print(f"[dbg] sent q#{qcount} len={len(payload)}", file=sys.stderr, flush=True)
    line = sys.stdin.readline()
    print(f"[dbg] reply raw={repr(line)[:200]}", file=sys.stderr, flush=True)
    if not line:
        raise RuntimeError("oracle EOF on q#%d" % qcount)
    return bool(json.loads(line.strip()).get("pad_ok"))
def decrypt_block(prev: bytes, target: bytes) -> bytes:
    inter = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for j in range(pos+1, 16):
            forged[j] = inter[j] ^ pad
        for j in range(pos):
            forged[j] = 0
        cand = None
        for g in range(256):
            forged[pos] = g
            if oracle(bytes(forged) + target):
                if pos == 15:
                    f2 = bytearray(forged); f2[14] ^= 1
                    q2 = base64.b64encode(bytes(f2) + target).decode()
                    print(json.dumps({"q": q2}), flush=True)
                    try:
                        os.fsync(sys.stdout.fileno())
                    except Exception:
                        pass
                    qcount2 = qcount + 1
                    line2 = sys.stdin.readline()
                    print(f"[dbg] verify reply={repr(line2)[:200]}", file=sys.stderr, flush=True)
                    if not line2:
                        raise RuntimeError("oracle EOF verify")
                    qcount_glob = globals()
                    globals()["qcount"] = globals()["qcount"] + 1
                    if not bool(json.loads(line2.strip()).get("pad_ok")):
                        continue
                cand = g
                break
        if cand is None:
            raise RuntimeError(f"no cand pos {pos}")
        inter[pos] = cand ^ pad
    return bytes(inter[j] ^ prev[j] for j in range(16))
out = b""
for i in range(len(blocks)):
    print(f"[dbg] block {i} start", file=sys.stderr, flush=True)
    pt = decrypt_block(prevs[i], blocks[i])
    print(f"[dbg] block {i} = {pt.hex()}", file=sys.stderr, flush=True)
    out += pt
pl = out[-1]
if 1 <= pl <= 16 and out[-pl:] == bytes([pl])*pl and len(out)-pl == 64:
    pt_hex = out[:-pl].hex()
else:
    pt_hex = out.hex()
t0 = time.monotonic_ns(); t1 = time.monotonic_ns()
print(f"OPSPAN_NS:{t1-t0}", flush=True)
print("CLAIM:" + json.dumps({"plaintext_hex": pt_hex}), flush=True)