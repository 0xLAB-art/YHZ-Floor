import sys, os, json, base64, select, time
ct_hex = "49324420443d10ce58309579924019bdc720e55149c31c71abd1b8b58b71bf0e2454b8c4f9ff0c8188a9f661a641d6fe9311cc187c0637e9369f0d9d38c870ad3c9c17737ad72a1a4fba62f937da9f7a"
iv_hex = "67c5f628f658cce21f1f0fdd2919bc3a"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
try:
    sys.stdout.reconfigure(line_buffering=True)
except:
    pass
STDOUT_FD = sys.stdout.fileno()
STDIN_FD = sys.stdin.fileno()
_read_buf = b""
def _send_line(s):
    data = (s + "\n").encode()
    os.write(STDOUT_FD, data)
    try:
        sys.stdout.flush()
    except:
        pass
def _recv_line(timeout=60):
    global _read_buf
    deadline = time.monotonic() + timeout
    while True:
        nl = _read_buf.find(b"\n")
        if nl >= 0:
            line = _read_buf[:nl]
            _read_buf = _read_buf[nl+1:]
            return line.decode(errors="replace")
        remain = deadline - time.monotonic()
        if remain <= 0:
            return None
        r, _, _ = select.select([STDIN_FD], [], [], min(1.0, remain))
        if not r:
            continue
        try:
            chunk = os.read(STDIN_FD, 65536)
        except Exception:
            time.sleep(0.05)
            continue
        if chunk is None or len(chunk) == 0:
            time.sleep(0.05)
            continue
        _read_buf += chunk
def oracle(fp, tg):
    b64 = base64.b64encode(fp + tg).decode()
    _send_line(json.dumps({"q": b64}))
    while True:
        line = _recv_line(timeout=60)
        if line is None:
            raise RuntimeError("oracle timeout")
        s = line.strip()
        if not s:
            continue
        try:
            o = json.loads(s)
        except:
            continue
        if "pad_ok" in o:
            return bool(o["pad_ok"])
        else:
            continue
def dec_block(targ):
    inter = [0]*16
    for pad in range(1, 17):
        pos = 16 - pad
        found = None
        for g in range(256):
            f = bytearray(16)
            for j in range(pos+1, 16):
                f[j] = inter[j] ^ pad
            f[pos] = g
            if oracle(bytes(f), targ):
                if pad == 1:
                    f2 = bytearray(f)
                    f2[14] ^= 1
                    if not oracle(bytes(f2), targ):
                        continue
                found = g
                break
        if found is None:
            raise RuntimeError("no pad byte found")
        inter[pos] = found ^ pad
    return bytes(inter)
t0 = time.monotonic_ns()
pts = []
for targ, prev in zip(blocks, prevs):
    inter = dec_block(targ)
    pts.append(bytes(a ^ b for a, b in zip(inter, prev)))
pt = b"".join(pts)
t1 = time.monotonic_ns()
_send_line("OPSPAN_NS:%d" % (t1 - t0))
_send_line("CLAIM:" + json.dumps({"plaintext_hex": pt.hex()}))