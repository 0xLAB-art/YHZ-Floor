import sys, json, base64, time

# ---------------------------------------------------------------------------
# Read provisioned data (single JSON line) from stdin.
# ---------------------------------------------------------------------------
prov_line = sys.stdin.readline()
if not prov_line:
    sys.exit(1)
prov = json.loads(prov_line)
CT_HEX = prov["ct_hex"]
IV_HEX = prov["iv_hex"]
BLOCK_SIZE = prov.get("block_size", 16)

# ---------------------------------------------------------------------------
# Padding‑oracle query helper.
# Sends a base64‑encoded 2‑block payload (forged_prev || target) and reads the
# oracle's JSON reply containing "pad_ok".
# ---------------------------------------------------------------------------
def query(forged_prev: bytes, target: bytes) -> bool:
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode()
    print(json.dumps({"q": b64}))
    sys.stdout.flush()
    resp_line = sys.stdin.readline()
    if not resp_line:
        sys.exit(1)
    resp = json.loads(resp_line)
    return bool(resp.get("pad_ok"))

# ---------------------------------------------------------------------------
# Recover a single plaintext block given the previous ciphertext block (or IV)
# and the current ciphertext block.
# ---------------------------------------------------------------------------
def recover_block(prev_ct: bytes, cur_ct: bytes) -> bytes:
    # intermediate = D_k(cur_ct)  (the raw CBC decryption output)
    intermediate = [0] * BLOCK_SIZE
    forged = bytearray(BLOCK_SIZE)
    for pos in range(BLOCK_SIZE - 1, -1, -1):
        pad_len = BLOCK_SIZE - pos
        # Adjust bytes that are already known so that they produce the required padding.
        for j in range(pos + 1, BLOCK_SIZE):
            forged[j] = intermediate[j] ^ pad_len
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), cur_ct):
                # When pad_len == 1 we may get a false positive (the original padding was 0x01).
                # Verify by flipping another byte and ensuring the padding now fails.
                if pad_len == 1:
                    test = bytearray(forged)
                    test[pos] ^= 0x01
                    if query(bytes(test), cur_ct):
                        continue  # false positive, keep searching
                intermediate[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at position {pos}")
    # Plaintext = intermediate XOR previous ciphertext (or IV)
    return bytes([intermediate[i] ^ prev_ct[i] for i in range(BLOCK_SIZE)])

# ---------------------------------------------------------------------------
# Main execution: split ciphertext into blocks, run the attack block‑by‑block.
# ---------------------------------------------------------------------------
def main():
    ct_bytes = bytes.fromhex(CT_HEX)
    iv_bytes = bytes.fromhex(IV_HEX)
    # Split ciphertext into 16‑byte blocks.
    ct_blocks = [ct_bytes[i:i+BLOCK_SIZE] for i in range(0, len(ct_bytes), BLOCK_SIZE)]
    # Prepend IV as block 0.
    blocks = [iv_bytes] + ct_blocks
    plaintext_parts = []
    start = time.monotonic_ns()
    for i in range(1, len(blocks)):
        pt_block = recover_block(blocks[i-1], blocks[i])
        plaintext_parts.append(pt_block)
    plaintext = b"".join(plaintext_parts)
    duration = time.monotonic_ns() - start
    # Output optional timing info (must appear before CLAIM).
    print(f"OPSPAN_NS:{duration}")
    # Final claim.
    claim = {"plaintext_hex": plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()