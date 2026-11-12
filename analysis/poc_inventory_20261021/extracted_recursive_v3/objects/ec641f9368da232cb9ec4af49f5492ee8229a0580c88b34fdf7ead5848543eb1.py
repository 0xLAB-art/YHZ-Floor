import sys, json, base64, time

# ---------- Helper I/O ----------
def read_json_line():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

def query(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    print(json.dumps({"q": b64}), flush=True)
    resp = read_json_line()
    return resp.get('pad_ok', False)

# ---------- Padding‑oracle block recovery ----------
def recover_intermediate(target_block: bytes, block_size: int) -> bytes:
    """Recover Dec_k(target_block) (the intermediate value) using the padding oracle.
    Returns a bytearray of length block_size.
    """
    intermediate = bytearray(block_size)
    # Work from last byte to first
    for pad_len in range(1, block_size + 1):
        idx = block_size - pad_len
        forged = bytearray(block_size)
        # Set bytes after idx to produce correct padding
        for i in range(idx + 1, block_size):
            forged[i] = intermediate[i] ^ pad_len
        found = False
        for guess in range(256):
            forged[idx] = guess ^ pad_len
            if query(bytes(forged), target_block):
                # Extra check for pad_len == 1 to avoid false positive when original padding was 0x01
                if pad_len == 1:
                    test = bytearray(forged)
                    test[(idx - 1) % block_size] ^= 0x01
                    if query(bytes(test), target_block):
                        # Still true → likely a false positive, continue searching
                        continue
                intermediate[idx] = guess
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at position {idx}")
    return bytes(intermediate)

# ---------- Main routine ----------
def main():
    # First line from stdin contains the provisioned material
    prov = read_json_line()
    ct_hex = prov['ct_hex']
    iv_hex = prov['iv_hex']
    block_size = prov.get('block_size', 16)

    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)

    # Split ciphertext into blocks (already includes the IV separately)
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]

    start_ns = time.monotonic_ns()
    plaintext_blocks = []
    prev = iv
    for blk in blocks:
        intermediate = recover_intermediate(blk, block_size)
        # Plaintext = intermediate XOR previous ciphertext (or IV for first block)
        plain = bytes(a ^ b for a, b in zip(intermediate, prev))
        plaintext_blocks.append(plain)
        prev = blk
    full_plain = b''.join(plaintext_blocks)

    # Strip PKCS#7 padding (verifier will also strip, but we do it for clarity)
    pad_len = full_plain[-1]
    if 1 <= pad_len <= block_size and full_plain[-pad_len:] == bytes([pad_len]) * pad_len:
        unpadded = full_plain[:-pad_len]
    else:
        unpadded = full_plain

    claim = {"plaintext_hex": unpadded.hex()}
    end_ns = time.monotonic_ns()
    print(f"OPSPAN_NS:{end_ns - start_ns}", flush=True)
    print(f"CLAIM:{json.dumps(claim)}", flush=True)

if __name__ == '__main__':
    main()