import sys, json, base64, time

# Hard‑coded provisioned data (from the task description)
CT_HEX = "c50421f08fee03b50a68433579af21e8a020733fb03275b0ebf272296d19afb7aa8accad4d7edf9cc50724309bc6b19da413f02bfe0d18fc12483869c87eced9f87c869073ad92ca169da9b23703e2f7"
IV_HEX = "80360e180bf2fc7f1b63a4e935c3a36b"
BLOCK_SIZE = 16

def query(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    print(json.dumps({"q": b64}))
    sys.stdout.flush()
    resp_line = sys.stdin.readline()
    if not resp_line:
        sys.exit(0)
    resp = json.loads(resp_line)
    return bool(resp.get("pad_ok"))

def recover_block(prev_ct: bytes, target_ct: bytes) -> bytes:
    block_size = BLOCK_SIZE
    intermediate = [0] * block_size
    forged = bytearray(block_size)
    for pos in range(block_size - 1, -1, -1):
        pad_len = block_size - pos
        # set bytes for already known positions to produce correct padding
        for j in range(pos + 1, block_size):
            forged[j] = intermediate[j] ^ pad_len
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target_ct):
                # For pad_len == 1, verify to avoid false positive
                if pad_len == 1:
                    # Change another byte (pos-1 if exists) and ensure padding fails
                    test_forged = bytearray(forged)
                    test_forged[pos] ^= 0x01
                    if query(bytes(test_forged), target_ct):
                        continue  # false positive, keep searching
                intermediate[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at position {pos}")
    # plaintext = intermediate XOR previous ciphertext (or IV)
    return bytes([intermediate[i] ^ prev_ct[i] for i in range(block_size)])

def main():
    ct_bytes = bytes.fromhex(CT_HEX)
    iv_bytes = bytes.fromhex(IV_HEX)
    # split ciphertext into 16‑byte blocks
    ct_blocks = [ct_bytes[i:i+BLOCK_SIZE] for i in range(0, len(ct_bytes), BLOCK_SIZE)]
    blocks = [iv_bytes] + ct_blocks
    plaintext_blocks = []
    start = time.monotonic_ns()
    for i in range(1, len(blocks)):
        pt = recover_block(blocks[i-1], blocks[i])
        plaintext_blocks.append(pt)
    plaintext = b"".join(plaintext_blocks)
    duration = time.monotonic_ns() - start
    claim = {"plaintext_hex": plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    # optional timing info (must appear before CLAIM to keep CLAIM last)
    # print(f"OPSPAN_NS:{duration}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()