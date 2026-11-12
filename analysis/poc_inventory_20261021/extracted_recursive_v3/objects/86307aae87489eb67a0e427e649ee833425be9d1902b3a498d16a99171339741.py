import sys, json, base64

ct_hex = "4427ab4844eaac13358587b1e41273837feb6a29f27baa8057bb1acb99766c4f0ac9c1e2a73bba4c2f48981a5895c83219a00dec1054b9d7e2b257719591ca7f441d3c27253f225054cf9b2ce60c215c"
iv_hex = "d2185f2da0c3bbe950043a87f5cd0333"
block_size = 16

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]

def oracle_query(forged_prev, target):
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode()
    print(json.dumps({"q": b64}), flush=True)
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)
    resp = json.loads(line)
    return resp.get("pad_ok", False)

intermediates = []
for idx, target in enumerate(blocks):
    prev_orig = iv if idx == 0 else blocks[idx-1]
    forged = bytearray(prev_orig)
    recovered = bytearray(block_size)
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        for j in range(block_size-1, pos, -1):
            forged[j] = recovered[j] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess ^ pad_val
            if oracle_query(bytes(forged), target):
                recovered[pos] = guess
                found = True
                break
        if not found:
            sys.stderr.write(f"Failed at block {idx} pos {pos}\n")
            sys.exit(1)
    intermediates.append(bytes(recovered))

plaintext_blocks = []
for i, I in enumerate(intermediates):
    prev = iv if i == 0 else blocks[i-1]
    plaintext_blocks.append(bytes(a ^ b for a, b in zip(I, prev)))

padded = b"".join(plaintext_blocks)
pad_len = padded[-1]
if 1 <= pad_len <= block_size and padded[-pad_len:] == bytes([pad_len])*pad_len:
    plaintext = padded[:-pad_len]
else:
    plaintext = padded

claim = {"plaintext_hex": plaintext.hex()}
print(f"CLAIM:{json.dumps(claim)}")