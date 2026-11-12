import sys, json, base64, time

# ----- Hard‑coded provisioned data -----
CT_HEX = "7642a01b1618f80267c233b518fa85aeaa7df3d23636f4bff45c8a701ca4375e135a508cad6fad83b3ec9209c7dac9ed6e1c7b103317d9ea230067ea48618c0d7dd75d7f3213088ef7e505f189768b35"
IV_HEX = "d3d0a0f2203b6d32f94602faa6573a0f"
BLOCK_SIZE = 16

ct_bytes = bytes.fromhex(CT_HEX)
iv_bytes = bytes.fromhex(IV_HEX)
blocks = [ct_bytes[i:i+BLOCK_SIZE] for i in range(0, len(ct_bytes), BLOCK_SIZE)]

# ----- I/O helpers -----
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

# ----- Padding‑oracle block recovery -----
def recover_intermediate(target_block: bytes) -> bytes:
    intermediate = bytearray(BLOCK_SIZE)
    for pad_len in range(1, BLOCK_SIZE + 1):
        idx = BLOCK_SIZE - pad_len
        forged = bytearray(BLOCK_SIZE)
        # set already‑known bytes to produce correct padding
        for i in range(idx + 1, BLOCK_SIZE):
            forged[i] = intermediate[i] ^ pad_len
        found = False
        for guess in range(256):
            forged[idx] = guess ^ pad_len
            if query(bytes(forged), target_block):
                # extra check for pad_len == 1 to avoid false positive when original padding was 0x01
                if pad_len == 1:
                    test = bytearray(forged)
                    test[(idx - 1) % BLOCK_SIZE] ^= 0x01
                    if query(bytes(test), target_block):
                        continue
                intermediate[idx] = guess
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at position {idx}")
    return bytes(intermediate)

# ----- Main attack -----
start_ns = time.monotonic_ns()
plaintext_blocks = []
prev = iv_bytes
for blk in blocks:
    inter = recover_intermediate(blk)
    plain = bytes(a ^ b for a, b in zip(inter, prev))
    plaintext_blocks.append(plain)
    prev = blk
full_plain = b''.join(plaintext_blocks)
# Strip PKCS#7 padding (verifier will also strip if we forget)
pad_len = full_plain[-1]
if 1 <= pad_len <= BLOCK_SIZE and full_plain[-pad_len:] == bytes([pad_len]) * pad_len:
    unpadded = full_plain[:-pad_len]
else:
    unpadded = full_plain
claim = {"plaintext_hex": unpadded.hex()}
end_ns = time.monotonic_ns()
# Only the CLAIM line is required as the final output
print(f"CLAIM:{json.dumps(claim)}", flush=True)