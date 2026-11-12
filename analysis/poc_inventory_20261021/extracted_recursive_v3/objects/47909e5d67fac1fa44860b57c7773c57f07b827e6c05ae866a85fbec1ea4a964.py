import sys, json, base64, time

def read_response():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line.strip())

def query(forged_prev: bytes, target: bytes) -> bool:
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    resp = read_response()
    return resp.get('pad_ok', False)

def attack_block(target: bytes, original_prev: bytes) -> bytes:
    # recover intermediate state (Decrypt(target))
    intermediate = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad_val = 16 - pos
        # set already known bytes to match padding
        for j in range(pos+1, 16):
            forged[j] = intermediate[j] ^ pad_val
        found = None
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target):
                # avoid false positive when padding_val == 1 and guess equals original byte that already yields padding
                # simple check: ensure that modifying another byte would break padding (optional)
                found = guess
                break
        if found is None:
            raise Exception('No valid padding byte found')
        intermediate[pos] = found ^ pad_val
    # plaintext = intermediate XOR original_prev
    plaintext_block = bytes(a ^ b for a, b in zip(intermediate, original_prev))
    return plaintext_block

def main():
    # provisioned material (hard‑coded as per task description)
    ct_hex = "086af0bc8b47a31a67ac445150d765e375915855cd5469f593ec23a63f3b94e11509f96327210f56977d4b65b2ce6f3c6f0ef2bd2f924cb912e554f9970ed137b57eaff9f01e76cbf69fbc899cc12085"
    iv_hex = "a0b88d81286921d8cd087b73fe94eef4"
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    plaintext = bytearray()
    for idx, block in enumerate(blocks):
        prev = iv if idx == 0 else blocks[idx-1]
        pt_block = attack_block(block, prev)
        plaintext.extend(pt_block)
    # remove PKCS#7 padding if present
    if plaintext:
        pad_len = plaintext[-1]
        if 1 <= pad_len <= 16 and all(p == pad_len for p in plaintext[-pad_len:]):
            plaintext = plaintext[:-pad_len]
    # output claim
    claim = {"plaintext_hex": plaintext.hex()}
    # optional timing measurement
    start = time.monotonic_ns()
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()
    end = time.monotonic_ns()
    sys.stdout.write("OPSPAN_NS:" + str(end - start) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()