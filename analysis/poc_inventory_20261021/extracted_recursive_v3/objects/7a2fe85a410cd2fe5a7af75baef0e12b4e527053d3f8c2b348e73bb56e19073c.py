import sys, json, base64, binascii, time, random

# Provisioned data
ct_hex = "4a86af17e70c9831d8ddcd95d96474ca5a7d2c74b09a156d4f99c688cf069be764609c69850fda86efa65bd03b093d9fb18597f94b7ecf55d0ef51cbecc543cab0e2728a8a6907b7d558b81192febba3"
iv_hex = "b7a2c144f8568b6dcd742bd9bd5c3240"
block_size = 16

ct_bytes = binascii.unhexlify(ct_hex)
iv_bytes = binascii.unhexlify(iv_hex)
blocks = [ct_bytes[i:i+block_size] for i in range(0, len(ct_bytes), block_size)]

# Function to query the padding oracle
def query_pad(forged_prev: bytes, target: bytes) -> bool:
    # both must be exactly one block
    data = forged_prev + target
    b64 = base64.b64encode(data).decode('ascii')
    # compact JSON without spaces
    sys.stdout.write(json.dumps({"q": b64}, separators=(',', ':')) + "\n")
    sys.stdout.flush()
    # read a single response line
    line = sys.stdin.readline()
    if not line:
        raise EOFError("Oracle closed")
    resp = json.loads(line.strip())
    return bool(resp.get("pad_ok", False))

intermediate_blocks = []
plaintext_blocks = []

for idx, target_block in enumerate(blocks):
    I = bytearray(block_size)
    forged = bytearray(block_size)
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        # set known suffix to enforce padding
        for j in range(pos+1, block_size):
            forged[j] = I[j] ^ pad_val
        found = False
        # try all 256 possibilities in random order
        guesses = list(range(256))
        random.shuffle(guesses)
        for guess in guesses:
            forged[pos] = guess
            if query_pad(bytes(forged), target_block):
                I[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            raise RuntimeError(f"Byte not recovered at block {idx} pos {pos}")
    intermediate_blocks.append(I)
    prev = iv_bytes if idx == 0 else blocks[idx-1]
    plaintext_blocks.append(bytes(a ^ b for a, b in zip(I, prev)))

full_plaintext = b"".join(plaintext_blocks)
plaintext_hex = binascii.hexlify(full_plaintext).decode('ascii')

# Report timing (optional)
start = time.monotonic_ns()
end = time.monotonic_ns()
sys.stdout.write(f"OPSPAN_NS:{end-start}\n")
# Final claim
claim = {"plaintext_hex": plaintext_hex}
sys.stdout.write("CLAIM:" + json.dumps(claim, separators=(',', ':')) + "\n")
sys.stdout.flush()