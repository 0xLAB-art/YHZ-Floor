import sys, json, base64, time

ct_hex = "6ff755bd50f8352f512e32f5249874d7e6d2f13741aeda98198af1dc2894780fbcd43cf785bae356de1fb2b2cd3cb5f167cc653942f931c9d72b82ff81a2735a29216f0b0f4a7316f765e6ec47177ccb"
iv_hex = "012ec4cc13b47691a144456ae84fce27"

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
block_size = 16

blocks = [ct[i*block_size:(i+1)*block_size] for i in range(len(ct)//block_size)]

def oracle_query(forged_prev: bytes, target_block: bytes) -> bool:
    query = forged_prev + target_block
    b64 = base64.b64encode(query).decode('ascii')
    print(json.dumps({"q": b64}))
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return False
    try:
        resp = json.loads(line)
        return bool(resp.get("pad_ok", False))
    except Exception:
        return False

def decrypt_block(target: bytes, prev: bytes):
    inter = [0]*block_size
    for pos in range(block_size-1, -1, -1):
        pad_len = block_size - pos
        forged = [0]*block_size
        for j in range(pos+1, block_size):
            forged[j] = inter[j] ^ pad_len
        found = None
        for guess in range(256):
            forged[pos] = guess ^ pad_len
            if oracle_query(bytes(forged), target):
                # verification
                forged2 = forged.copy()
                forged2[pos] = (guess ^ 0x01) ^ pad_len
                if not oracle_query(bytes(forged2), target):
                    found = guess
                    break
        if found is None:
            for guess in range(256):
                forged[pos] = guess ^ pad_len
                if oracle_query(bytes(forged), target):
                    found = guess
                    break
            if found is None:
                raise ValueError("Failed to solve byte")
        inter[pos] = found
    inter_bytes = bytes(inter)
    plain = bytes([inter_bytes[i] ^ prev[i] for i in range(block_size)])
    return inter_bytes, plain

start = time.monotonic_ns()
prev = iv
plaintext_blocks = []
for target in blocks:
    _, p = decrypt_block(target, prev)
    plaintext_blocks.append(p)
    prev = target
plaintext_padded = b''.join(plaintext_blocks)
# remove PKCS#7 padding
pad_byte = plaintext_padded[-1]
if 1 <= pad_byte <= block_size:
    plaintext = plaintext_padded[:-pad_byte]
else:
    plaintext = plaintext_padded  # fallback

print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext.hex()})}")
# optional ops span
end = time.monotonic_ns()
print(f"OPSPAN_NS:{end - start}")