import sys, json, base64

# ----- Provisioned data -----
ct_hex = "4427ab4844eaac13358587b1e41273837feb6a29f27baa8057bb1acb99766c4f0ac9c1e2a73bba4c2f48981a5895c83219a00dec1054b9d7e2b257719591ca7f441d3c27253f225054cf9b2ce60c215c"
iv_hex = "d2185f2da0c3bbe950043a87f5cd0333"
block_size = 16

# Convert hex strings to bytes (guard against malformed input)
try:
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
except Exception as e:
    # If conversion fails, output empty claim to satisfy protocol
    print(f"CLAIM:{json.dumps({{'plaintext_hex': ''}})}")
    sys.exit(0)

# Split ciphertext into 16‑byte blocks
blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]

# ----- Padding‑oracle interaction -----
def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    """Send a query to the verifier and return True if padding is valid."""
    payload = forged_prev + target  # 32 bytes total
    b64 = base64.b64encode(payload).decode()
    print(json.dumps({"q": b64}), flush=True)
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)  # no response -> abort
    resp = json.loads(line)
    return bool(resp.get("pad_ok"))

# ----- Recover intermediate values (D_k(C_i)) -----
intermediates = []  # one entry per ciphertext block
for idx, target_block in enumerate(blocks):
    # Original previous block (or IV for the first block)
    prev_orig = iv if idx == 0 else blocks[idx-1]
    forged = bytearray(prev_orig)          # mutable copy we will modify
    recovered = bytearray(block_size)      # will hold the intermediate bytes
    # Recover bytes from last to first
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        # Adjust already‑known suffix to match the required padding value
        for j in range(block_size-1, pos, -1):
            forged[j] = recovered[j] ^ pad_val
        # Brute‑force the current byte
        found = False
        for guess in range(256):
            forged[pos] = guess ^ pad_val
            if oracle_query(bytes(forged), target_block):
                recovered[pos] = guess
                found = True
                break
        if not found:
            sys.stderr.write(f"[!] Failed to recover byte at block {idx}, position {pos}\n")
            sys.exit(1)
    intermediates.append(bytes(recovered))

# ----- Derive plaintext from intermediates -----
plaintext_blocks = []
for i, I in enumerate(intermediates):
    prev = iv if i == 0 else blocks[i-1]
    plaintext_blocks.append(bytes(a ^ b for a, b in zip(I, prev)))

padded_plaintext = b"".join(plaintext_blocks)
# Remove PKCS#7 padding if it looks valid
pad_len = padded_plaintext[-1]
if 1 <= pad_len <= block_size and padded_plaintext[-pad_len:] == bytes([pad_len]) * pad_len:
    plaintext = padded_plaintext[:-pad_len]
else:
    plaintext = padded_plaintext

# ----- Final claim -----
claim = {"plaintext_hex": plaintext.hex()}
print(f"CLAIM:{json.dumps(claim)}", flush=True)
sys.exit(0)