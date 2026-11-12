import sys, json, base64, time

# Hard‑coded provisioned values (as given in the task description)
ct_hex = "619589d0c229e2cdcc3f9c10c5bc83bc71f885e710dbb56ad74d47fac1b62e13ae5729eeb441aa52d323e67f222b681d330b0759ef59d4e0b4eeaa42b23a79767159aff13847223032d84bc43151bebe"
iv_hex = "24c406f885186989a9ae1f71f0ca8a7f"
block_size = 16

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]  # ciphertext blocks (5 blocks)

# Oracle query function: send forged_prev||target (32 bytes) and read pad_ok response
def query(forged_prev: bytes, target: bytes) -> bool:
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)
    resp = json.loads(line)
    return resp.get("pad_ok", False)

recovered_blocks = []
prev = iv
for target_block in blocks:
    recovered = bytearray(block_size)
    forged = bytearray(block_size)
    # Recover bytes from last to first
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        # Adjust already recovered positions to produce correct padding value
        for j in range(block_size-1, pos, -1):
            forged[j] = recovered[j] ^ pad_val
        # Brute‑force the current byte
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target_block):
                # plaintext byte = guess XOR pad_val
                recovered[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            sys.stderr.write(f"Failed to recover byte at position {pos}\n")
            sys.exit(1)
    recovered_blocks.append(bytes(recovered))
    prev = target_block

plaintext = b''.join(recovered_blocks)
claim = {"plaintext_hex": plaintext.hex()}
# Final claim line
sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
sys.stdout.flush()