import sys, json, base64, time

# Read the provisioned JSON line (contains ct_hex, iv_hex, etc.)
prov_line = sys.stdin.readline()
if not prov_line:
    sys.exit(0)
prov = json.loads(prov_line)
CT_HEX = prov["ct_hex"]
IV_HEX = prov["iv_hex"]
BLOCK_SIZE = prov.get("block_size", 16)

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
    intermediate = [0] * BLOCK_SIZE
    forged = bytearray(BLOCK_SIZE)
    for pos in range(BLOCK_SIZE - 1, -1, -1):
        pad_len = BLOCK_SIZE - pos
        # set already known positions to produce correct padding
        for j in range(pos + 1, BLOCK_SIZE):
            forged[j] = intermediate[j] ^ pad_len
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target_ct):
                # For pad_len == 1, verify to avoid false positive
                if pad_len == 1:
                    # Flip another byte (if any) and ensure padding fails
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
    return bytes([intermediate[i] ^ prev_ct[i] for i in range(BLOCK_SIZE)])

def main():
    ct_bytes = bytes.fromhex(CT_HEX)
    iv_bytes = bytes.fromhex(IV_HEX)
    # split ciphertext into blocks
    ct_blocks = [ct_bytes[i:i+BLOCK_SIZE] for i in range(0, len(ct_bytes), BLOCK_SIZE)]
    blocks = [iv_bytes] + ct_blocks
    plaintext_blocks = []
    start_ns = time.monotonic_ns()
    for i in range(1, len(blocks)):
        pt_block = recover_block(blocks[i-1], blocks[i])
        plaintext_blocks.append(pt_block)
    plaintext = b"".join(plaintext_blocks)
    duration_ns = time.monotonic_ns() - start_ns
    # Optional timing info (must appear before CLAIM as CLAIM must be last line)
    print(f"OPSPAN_NS:{duration_ns}")
    claim = {"plaintext_hex": plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()