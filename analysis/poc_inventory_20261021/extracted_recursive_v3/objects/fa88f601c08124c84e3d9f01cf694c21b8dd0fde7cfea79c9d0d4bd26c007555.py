import sys, json, base64, time

# Provisioned data (hard‑coded from the task description)
CT_HEX = "7642a01b1618f80267c233b518fa85aeaa7df3d23636f4bff45c8a701ca4375e135a508cad6fad83b3ec9209c7dac9ed6e1c7b103317d9ea230067ea48618c0d7dd75d7f3213088ef7e505f189768b35"
IV_HEX = "d3d0a0f2203b6d32f94602faa6573a0f"
BLOCK_SIZE = 16

ct_bytes = bytes.fromhex(CT_HEX)
iv_bytes = bytes.fromhex(IV_HEX)

# Split ciphertext into 16‑byte blocks (the IV is separate)
blocks = [ct_bytes[i:i+BLOCK_SIZE] for i in range(0, len(ct_bytes), BLOCK_SIZE)]

def read_response():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

def query(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    print(json.dumps({"q": b64}), flush=True)
    resp = read_response()
    return resp.get('pad_ok', False)

def recover_block(target_block: bytes, prev_block: bytes) -> bytes:
    """Recover the intermediate state D_i = Dec_k(target_block) for one block.
    Returns the 16‑byte intermediate value.
    """
    intermediate = bytearray(BLOCK_SIZE)
    # work from last byte to first
    for pad_len in range(1, BLOCK_SIZE + 1):
        idx = BLOCK_SIZE - pad_len
        # Build forged_prev with already‑recovered bytes set to produce correct padding
        forged = bytearray(BLOCK_SIZE)
        for i in range(idx + 1, BLOCK_SIZE):
            forged[i] = intermediate[i] ^ pad_len
        found = False
        for guess in range(256):
            forged[idx] = guess ^ pad_len
            # other bytes (0..idx-1) stay zero for now
            if query(bytes(forged), target_block):
                # For pad_len == 1 we need to rule out the rare false‑positive where the original padding was 0x01.
                if pad_len == 1:
                    # Change a different byte (e.g., idx-1) and expect the padding check to fail.
                    test_forged = bytearray(forged)
                    test_forged[(idx - 1) % BLOCK_SIZE] ^= 0x01
                    if query(bytes(test_forged), target_block):
                        # Still true → likely a false positive, continue searching.
                        continue
                intermediate[idx] = guess
                found = True
                break
        if not found:
            raise RuntimeError('Failed to recover byte at position {}'.format(idx))
    return bytes(intermediate)

def main():
    start_ns = time.monotonic_ns()
    plaintext_blocks = []
    prev = iv_bytes
    for blk in blocks:
        di = recover_block(blk, prev)
        pi = bytes(a ^ b for a, b in zip(di, prev))
        plaintext_blocks.append(pi)
        prev = blk
    full_plain = b''.join(plaintext_blocks)
    # Strip PKCS#7 padding (the verifier will also strip if we forget)
    pad_len = full_plain[-1]
    if 1 <= pad_len <= BLOCK_SIZE and full_plain[-pad_len:] == bytes([pad_len]) * pad_len:
        unpadded = full_plain[:-pad_len]
    else:
        unpadded = full_plain
    claim = {"plaintext_hex": unpadded.hex()}
    end_ns = time.monotonic_ns()
    print(f"OPSPAN_NS:{end_ns - start_ns}", flush=True)
    print(f"CLAIM:{json.dumps(claim)}", flush=True)

if __name__ == '__main__':
    main()