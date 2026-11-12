import sys, json, base64, binascii, time

def read_input():
    # The provisioned material is passed via stdin at start as a JSON line
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

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
    block_size = 16
    intermediate = [0] * block_size  # D_k(target_ct)
    forged = bytearray(block_size)
    for pos in range(block_size - 1, -1, -1):
        pad_len = block_size - pos
        # set already discovered bytes to produce correct padding
        for j in range(pos + 1, block_size):
            forged[j] = intermediate[j] ^ pad_len
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target_ct):
                # handle possible false positive when padding_len == 1
                # verify by changing another byte if needed
                intermediate[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError("Failed to recover a byte at position {}".format(pos))
    # plaintext = intermediate XOR previous ciphertext block (or IV)
    plaintext = bytes([intermediate[i] ^ prev_ct[i] for i in range(block_size)])
    return plaintext

def main():
    prov = read_input()
    ct_bytes = bytes.fromhex(prov["ct_hex"])
    iv_bytes = bytes.fromhex(prov["iv_hex"])
    block_size = prov.get("block_size", 16)
    # split ciphertext into blocks
    ct_blocks = [ct_bytes[i:i+block_size] for i in range(0, len(ct_bytes), block_size)]
    # prepend IV as block 0
    blocks = [iv_bytes] + ct_blocks
    plaintext_blocks = []
    start_ns = time.monotonic_ns()
    for i in range(1, len(blocks)):
        pt_block = recover_block(blocks[i-1], blocks[i])
        plaintext_blocks.append(pt_block)
    plaintext = b"".join(plaintext_blocks)
    end_ns = time.monotonic_ns()
    # output claim
    claim = {"plaintext_hex": plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    # optional timing info
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()