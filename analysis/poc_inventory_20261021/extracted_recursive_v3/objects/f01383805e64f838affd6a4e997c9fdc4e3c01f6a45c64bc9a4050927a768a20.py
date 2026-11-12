import sys, json, base64, time

def read_json_line():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line.rstrip('\n'))

def query(forged_prev: bytes, target: bytes) -> bool:
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode()
    # send query
    print(json.dumps({"q": b64}, separators=(',', ':')), flush=True)
    # read oracle response
    resp = read_json_line()
    return resp.get('pad_ok', False)

def recover_block(target: bytes, prev: bytes) -> bytes:
    bs = 16
    if len(target) != bs or len(prev) != bs:
        raise ValueError('Block size mismatch')
    # intermediate bytes I = D_k(C_i)
    intermediate = [0] * bs
    forged = bytearray(bs)
    for pos in range(bs - 1, -1, -1):
        pad_val = bs - pos
        # set bytes after pos to produce correct padding
        for j in range(pos + 1, bs):
            forged[j] = prev[j] ^ intermediate[j] ^ pad_val
        found = False
        for guess in range(256):
            # guess is the intermediate byte value
            forged[pos] = prev[pos] ^ guess ^ pad_val
            if query(bytes(forged), target):
                # When pad_val == 1, a false positive can occur (original padding already 0x01).
                # Verify by flipping another byte.
                if pad_val == 1:
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
            raise RuntimeError(f'Failed to recover byte at position {pos}')
    # plaintext = intermediate XOR prev
    return bytes(i ^ p for i, p in zip(intermediate, prev))

def main():
    # read provisioned material (first line from stdin)
    prov = read_json_line()
    ct = bytes.fromhex(prov['ct_hex'])
    iv = bytes.fromhex(prov['iv_hex'])
    block_size = prov.get('block_size', 16)
    # split ciphertext into blocks
    blocks = [iv] + [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    start = time.monotonic_ns()
    for i in range(1, len(blocks)):
        pt_block = recover_block(blocks[i], blocks[i-1])
        plaintext_blocks.append(pt_block)
    plaintext = b''.join(plaintext_blocks)
    end = time.monotonic_ns()
    # optional timing output
    print(f"OPSPAN_NS:{end-start}", flush=True)
    claim = {"plaintext_hex": plaintext.hex()}
    print('CLAIM:' + json.dumps(claim, separators=(',', ':')), flush=True)

if __name__ == '__main__':
    main()