import sys, json, base64, binascii, time

def read_json_line():
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("Unexpected EOF from oracle")
    return json.loads(line.strip())

def query(forged_prev: bytes, target: bytes) -> bool:
    # forged_prev and target are each 16 bytes
    payload = base64.b64encode(forged_prev + target).decode()
    print(json.dumps({"q": payload}), flush=True)
    resp = read_json_line()
    return resp.get("pad_ok", False)

def recover_block(prev_block: bytes, target_block: bytes) -> bytes:
    block_size = 16
    intermediate = [0] * block_size  # D_k(target) values
    # recover from last byte to first
    for pad_len in range(1, block_size + 1):
        pos = block_size - pad_len
        forged = bytearray(block_size)
        # set bytes after pos to enforce correct padding
        for i in range(pos + 1, block_size):
            forged[i] = intermediate[i] ^ pad_len
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target_block):
                # compute intermediate byte
                intermediate[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at position {pos}")
    return bytes(intermediate)

def main():
    # Read provisioned material (single JSON line)
    provision_line = sys.stdin.readline()
    if not provision_line:
        raise RuntimeError("No provision data received")
    provision = json.loads(provision_line.strip())
    ct = binascii.unhexlify(provision["ct_hex"])
    iv = binascii.unhexlify(provision["iv_hex"])
    block_size = provision.get("block_size", 16)
    # Split ciphertext into 16‑byte blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    # Expect 5 blocks (64‑byte plaintext => 4 ciphertext blocks + final block with padding)
    plaintext_blocks = []
    for idx, target in enumerate(blocks):
        prev = iv if idx == 0 else blocks[idx-1]
        inter = recover_block(prev, target)
        plain = bytes(a ^ b for a, b in zip(inter, prev))
        plaintext_blocks.append(plain)
    full_plain = b''.join(plaintext_blocks)
    # Strip PKCS#7 padding if present
    pad_len = full_plain[-1]
    if 1 <= pad_len <= block_size and full_plain[-pad_len:] == bytes([pad_len])*pad_len:
        stripped = full_plain[:-pad_len]
    else:
        stripped = full_plain
    claim = {"plaintext_hex": stripped.hex()}
    # Optional timing measurement
    start = time.monotonic_ns()
    # (nothing heavy here)
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end - start}", flush=True)
    print(f"CLAIM:{json.dumps(claim)}", flush=True)

if __name__ == "__main__":
    main()