import sys, json, base64, time

# Provisioned data
ct_hex = "597ffc05ced12ea900dc1c68a308271272049f17fe8503e93cae0dfb069473d1185e1d67aa85c7d84678c299e008039eab8191074f28c129c590568508ba834056916a4fbeddc41c923577a28cecc381"
iv_hex = "bb15c9e0f618383a43257ed3bf54754d"
block_size = 16

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]

# Communication helpers
def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    # forged_prev and target are each block_size bytes
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)
    resp = json.loads(line)
    return resp.get("pad_ok", False)

plaintext_blocks = []
start_ns = time.monotonic_ns()

for idx, target in enumerate(blocks):
    prev = iv if idx == 0 else blocks[idx-1]
    intermediate = bytearray(block_size)
    # recover each byte from last to first
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        # set known suffix bytes to produce correct padding
        forged = bytearray(block_size)
        for j in range(pos+1, block_size):
            forged[j] = intermediate[j] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess
            if oracle_query(bytes(forged), target):
                # found a byte that yields correct padding
                intermediate[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            # Should not happen; abort
            sys.stderr.write(f"Failed to recover byte at block {idx}, position {pos}\n")
            sys.exit(1)
    # compute plaintext block
    plain_block = bytes(a ^ b for a, b in zip(intermediate, prev))
    plaintext_blocks.append(plain_block)

plaintext = b"".join(plaintext_blocks)
end_ns = time.monotonic_ns()

# Output claim
claim = {"plaintext_hex": plaintext.hex()}
sys.stdout.write(f"CLAIM:{json.dumps(claim)}\n")
# optional timing
sys.stdout.write(f"OPSPAN_NS:{end_ns - start_ns}\n")
sys.stdout.flush()