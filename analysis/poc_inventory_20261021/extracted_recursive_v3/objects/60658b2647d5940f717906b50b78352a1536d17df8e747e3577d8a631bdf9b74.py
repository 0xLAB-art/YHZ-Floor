import sys, base64, json, time

def read_response():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

def query(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    # compact JSON without spaces
    print(json.dumps({"q": b64}, separators=(',', ':')), flush=True)
    resp = read_response()
    return resp.get('pad_ok', False)

def recover_block(target: bytes, prev_known: bytes) -> bytes:
    block_size = 16
    intermediate = [0] * block_size  # I = D_k(C_i)
    forged = bytearray(block_size)
    for pos in range(block_size - 1, -1, -1):
        pad_val = block_size - pos
        # set bytes after pos to enforce padding
        for j in range(pos + 1, block_size):
            forged[j] = prev_known[j] ^ intermediate[j] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = prev_known[pos] ^ guess ^ pad_val
            if query(bytes(forged), target):
                # verify when pad_val == 1 to avoid false positive
                if pad_val == 1:
                    # flip another byte and re‑query
                    forged[pos] ^= 1
                    if not query(bytes(forged), target):
                        forged[pos] ^= 1
                        intermediate[pos] = guess ^ pad_val
                        found = True
                        break
                    forged[pos] ^= 1
                intermediate[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at position {pos}")
    # plaintext = intermediate XOR prev_known
    return bytes(i ^ p for i, p in zip(intermediate, prev_known))

def main():
    ct_hex = "4da13dfa23b340d64743476bda799dfafd37b7090f503698b796976faadc74e02d6e8a589fabb9e460ec83d99c5bd311ef4795b29c305d3ae0c075e70643f0fb72b2b5fee21dd4279c95184cddb1a443"
    iv_hex = "b77356ac6815e29b39a40ec792042ee3"
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    # split ciphertext into 16‑byte blocks
    blocks = [iv] + [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    start = time.monotonic_ns()
    for i in range(1, len(blocks)):
        pt = recover_block(blocks[i], blocks[i-1])
        plaintext_blocks.append(pt)
    plaintext = b''.join(plaintext_blocks)
    end = time.monotonic_ns()
    # report timing (optional)
    print(f"OPSPAN_NS:{end-start}", flush=True)
    claim = {"plaintext_hex": plaintext.hex()}
    print('CLAIM:' + json.dumps(claim, separators=(',', ':')), flush=True)

if __name__ == '__main__':
    main()