import sys, os, json, base64, time
ct_hex = "ee0b7104daa977e1e0a569e8d0cd3fab6f1d615090b7a2a5b08cf2e37874cd6d45390a1f0816ab2685c8e224248343d5c3467daa8dba078f8415d0eeb59e968bb619d0a6a9dd7de14208fd731876eff4"
iv_hex = "22da83b7a1b1ffca86c9858602190b37"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
t0 = time.monotonic_ns()
err = sys.stderr
def ask(fprev, tgt):
    data = bytes(fprev) + bytes(tgt)
    b64 = base64.b64encode(data).decode()
    msg = '{"q": "' + b64 + '"}\n'
    os.write(1, msg.encode())
    try:
        os.fsync(1)
    except Exception:
        pass
    line = sys.stdin.buffer.readline()
    if not line:
        raise RuntimeError("EOF from oracle")
    try:
        obj = json.loads(line.decode())
    except Exception as e:
        print(f"BADREPLY:{line!r} err={e}", file=err, flush=True)
        raise
    return bool(obj.get("pad_ok"))
try:
    # sanity probe logged to stderr
    print(f"BLOCKS={len(blocks)} CTLEN={len(ct)}", file=err, flush=True)
    pts = []
    for bi, (tgt, prv) in enumerate(zip(blocks, prevs)):
        inter = bytearray(16)
        forged = bytearray(16)
        for pad in range(1, 17):
            pos = 16 - pad
            for j in range(pos+1, 16):
                forged[j] = inter[j] ^ pad
            for j in range(pos):
                forged[j] = 0
            found = None
            for g in range(256):
                forged[pos] = g
                ok = ask(forged, tgt)
                if ok:
                    if pad == 1:
                        sv = forged[14]
                        forged[14] ^= 1
                        ok2 = ask(forged, tgt)
                        forged[14] = sv
                        if not ok2:
                            continue
                    found = g
                    break
            if found is None:
                raise RuntimeError(f"block {bi} pad {pad}: no guess")
            inter[pos] = found ^ pad
        pt = bytes(a ^ b for a, b in zip(bytes(inter), prv))
        pts.append(pt)
        print(f"BLOCK{bi} OK: {pt.hex()}", file=err, flush=True)
    padded = b"".join(pts)
    print(f"PADDED:{padded.hex()}", file=err, flush=True)
except Exception as e:
    import traceback
    traceback.print_exc(file=err)
    try:
        padded
    except NameError:
        padded = b"\x00" * 80
t1 = time.monotonic_ns()
try:
    os.write(1, f"OPSPAN_NS:{t1-t0}\n".encode())
except Exception:
    pass
os.write(1, ("CLAIM:" + json.dumps({"plaintext_hex": padded.hex()}) + "\n").encode())