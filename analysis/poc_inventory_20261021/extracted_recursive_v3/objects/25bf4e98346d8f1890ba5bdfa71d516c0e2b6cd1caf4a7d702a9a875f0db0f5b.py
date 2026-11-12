import sys, json, base64, time
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
ct_hex = "4a56043aafdab687b845e5e83866d3998a029d8983c19441cd5e00bdb5c608d95f9981f01256e6e889bb76e9c592bd37fd16475b77d788ff7b2e37c12831f6c7e0743350ddf0a38fc647f5d41c3dce55"
iv_hex = "84944aaacfa463714374001e6e8e5bcc"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prev_blocks = [iv] + blocks[:-1]
qcount = 0
def query(forged_prev: bytes, target: bytes):
    global qcount
    b64 = base64.b64encode(forged_prev + target).decode()
    line = json.dumps({"q": b64})
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
    qcount += 1
    print(f"sent q#{qcount} len={len(forged_prev+target)}", file=sys.stderr, flush=True)
    resp = sys.stdin.readline()
    print(f"recv q#{qcount}: {resp!r}", file=sys.stderr, flush=True)
    if not resp:
        raise RuntimeError("empty oracle reply (EOF)")
    obj = json.loads(resp)
    return bool(obj.get("pad_ok"))
def recover_intermediate(target: bytes):
    inter = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for k in range(pos+1, 16):
            forged[k] = inter[k] ^ pad
        found = None
        for g in range(256):
            forged[pos] = g ^ pad
            ok = query(bytes(forged), target)
            if ok:
                if pad == 1:
                    sv = forged[pos-1]
                    forged[pos-1] = sv ^ 0x01
                    ok2 = query(bytes(forged), target)
                    forged[pos-1] = sv
                    if not ok2:
                        continue
                found = g
                break
        if found is None:
            raise RuntimeError(f"no valid byte at pos {pos}")
        inter[pos] = found
        print(f"pos {pos} -> {found:02x}", file=sys.stderr, flush=True)
    return bytes(inter)
try:
    t0 = time.monotonic_ns()
    pts = []
    for idx, tgt in enumerate(blocks):
        print(f"attack block {idx}", file=sys.stderr, flush=True)
        inter = recover_intermediate(tgt)
        print(f"inter {idx}: {inter.hex()}", file=sys.stderr, flush=True)
        pt = bytes(a ^ b for a, b in zip(inter, prev_blocks[idx]))
        pts.append(pt)
    full = b"".join(pts)
    t1 = time.monotonic_ns()
    padlen = full[-1]
    if 1 <= padlen <= 16 and full[-padlen:] == bytes([padlen])*padlen:
        out = full[:-padlen]
    else:
        out = full
    print(f"FULL {full.hex()}", file=sys.stderr, flush=True)
    sys.stdout.write(f"OPSPAN_NS:{t1-t0}\n")
    sys.stdout.flush()
    sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": out.hex()}) + "\n")
    sys.stdout.flush()
except Exception as e:
    print(f"ERROR {e!r} after {qcount} queries", file=sys.stderr, flush=True)
    import traceback; traceback.print_exc(file=sys.stderr)
    sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": "00"*64}) + "\n")
    sys.stdout.flush()