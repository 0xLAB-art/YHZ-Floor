import sys, json, base64, time

def read_json_line():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line.strip())

def query(forged_prev: bytes, target: bytes) -> bool:
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    resp = read_json_line()
    return bool(resp.get('pad_ok', False))

def attack_block(target: bytes, prev_cipher: bytes) -> bytes:
    # Recover intermediate state (Decrypt(target)) using padding oracle
    intermediate = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad_val = 16 - pos
        # set already known bytes to produce correct padding
        for j in range(pos + 1, 16):
            forged[j] = intermediate[j] ^ pad_val
        found = None
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target):
                if pad_val == 1:
                    # Disambiguate possible false positive for padding=1
                    forged[pos] ^= 1
                    if not query(bytes(forged), target):
                        forged[pos] ^= 1
                        found = guess
                        break
                    forged[pos] ^= 1
                else:
                    found = guess
                    break
        if found is None:
            raise RuntimeError('Failed to find valid padding byte')
        intermediate[pos] = found ^ pad_val
    # Plaintext block = intermediate XOR previous ciphertext (or IV)
    return bytes(a ^ b for a, b in zip(intermediate, prev_cipher))

def main():
    # Read the provisioned JSON (contains ct_hex, iv_hex, etc.)
    prov = read_json_line()
    ct = bytes.fromhex(prov['ct_hex'])
    iv = bytes.fromhex(prov['iv_hex'])
    # Split ciphertext into 16‑byte blocks
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    plaintext = bytearray()
    for idx, block in enumerate(blocks):
        prev = iv if idx == 0 else blocks[idx-1]
        pt_block = attack_block(block, prev)
        plaintext.extend(pt_block)
    # Remove PKCS#7 padding if present
    if plaintext:
        pad_len = plaintext[-1]
        if 1 <= pad_len <= 16 and all(p == pad_len for p in plaintext[-pad_len:]):
            plaintext = plaintext[:-pad_len]
    claim = {"plaintext_hex": plaintext.hex()}
    start = time.monotonic_ns()
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()
    end = time.monotonic_ns()
    sys.stdout.write("OPSPAN_NS:" + str(end - start) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()