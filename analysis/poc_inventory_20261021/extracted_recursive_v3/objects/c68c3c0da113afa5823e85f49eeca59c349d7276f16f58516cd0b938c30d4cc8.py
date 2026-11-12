import sys, json, base64, time
ct_hex = "925cca7774cccd61f712516d5a187fa6bdb83d3e282f0d4335229e4262bce0a173f1b965d01216bf5a6720bade071bc3483a0e92ce46905729ca99d7a937066009a3684364b5f36ae0273f5e42b44fec"
iv_hex = "7ea8ee1a4835aaea44729adcbc475b60"
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
ct_blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
last_dt = [0]

def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    payload = base64.b64encode(forged_prev + target).decode()
    sys.stdout.write(json.dumps({"q": payload}) + "\n")
    sys.stdout.flush()
    t0 = time.monotonic_ns()
    line = sys.stdin.readline()
    t1 = time.monotonic_ns()
    last_dt[0] = t1 - t0
    if not line:
        raise EOFError("oracle EOF")
    obj = json.loads(line.strip())
    return bool(obj.get("pad_ok"))

def recover_intermediate(target: bytes) -> bytes:
    I = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad_len = 16 - pos
        for k in range(pos+1, 16):
            forged[k] = I[k] ^ pad_len
        found = None
        for guess in range(256):
            forged[pos] = guess
            ok = oracle_query(bytes(forged), target)
            if ok:
                if pad_len == 1:
                    forged2 = bytearray(forged)
                    forged2[14] ^= 0x01
                    ok2 = oracle_query(bytes(forged2), target)
                    if not ok2:
                        continue
                found = guess
                break
        if found is None:
            raise RuntimeError(f"no valid padding found pos={pos}")
        I[pos] = found ^ pad_len
        # reset prefix handling: keep forged prefix as is for next iter (will be overwritten)
    return bytes(I)

plaintext_blocks = []
for idx, target in enumerate(ct_blocks):
    prev = iv if idx == 0 else ct_blocks[idx-1]
    I = recover_intermediate(target)
    P = bytes(a ^ b for a, b in zip(I, prev))
    plaintext_blocks.append(P)

padded = b"".join(plaintext_blocks)
# sanity: verify PKCS7 (last block should be 16x0x10 if 64-byte msg, but accept whatever)
# strip not needed; claim padded hex (verifier strips)
pt_hex = padded.hex()
# OPSPAN must be measured around last op; last_dt holds last query duration
try:
    dt = int(last_dt[0])
except:
    dt = 0
if dt <= 0:
    dt = 1
sys.stdout.write(f"OPSPAN_NS:{dt}\n")
sys.stdout.flush()
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": pt_hex}, separators=(',', ':')) + "\n")
sys.stdout.flush()