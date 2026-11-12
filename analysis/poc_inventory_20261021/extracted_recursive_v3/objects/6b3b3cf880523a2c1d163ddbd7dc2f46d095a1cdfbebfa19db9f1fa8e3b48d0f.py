import sys, json, base64, time

# Provisioned data
ct_hex = "619589d0c229e2cdcc3f9c10c5bc83bc71f885e710dbb56ad74d47fac1b62e13ae5729eeb441aa52d323e67f222b681d330b0759ef59d4e0b4eeaa42b23a79767159aff13847223032d84bc43151bebe"
iv_hex = "24c406f885186989a9ae1f71f0ca8a7f"
block_size = 16

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]  # 5 ciphertext blocks

# Oracle query function
def query(forged_prev: bytes, target: bytes) -> bool:
    assert len(forged_prev) == block_size and len(target) == block_size
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
prev_block = iv
for idx, target_block in enumerate(blocks):
    # Recover plaintext for this block
    recovered = bytearray(block_size)
    forged = bytearray(block_size)
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        # set bytes after pos to enforce padding
        for j in range(block_size-1, pos, -1):
            forged[j] = recovered[j] ^ pad_val
        # try all possible byte values
        found = None
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target_block):
                # compute plaintext byte
                plain_byte = guess ^ pad_val
                recovered[pos] = plain_byte
                found = guess
                break
        if found is None:
            # Should not happen
            sys.stderr.write(f"Failed to recover byte at block {idx} pos {pos}\n")
            sys.exit(1)
    recovered_blocks.append(bytes(recovered))
    prev_block = target_block

plaintext = b''.join(recovered_blocks)
plaintext_hex = plaintext.hex()
# Output final claim
claim = {"plaintext_hex": plaintext_hex}
sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
# optional timing measurement
ops_end = time.monotonic_ns()
sys.stdout.write("OPSPAN_NS:" + str(ops_end) + "\n")
sys.stdout.flush()