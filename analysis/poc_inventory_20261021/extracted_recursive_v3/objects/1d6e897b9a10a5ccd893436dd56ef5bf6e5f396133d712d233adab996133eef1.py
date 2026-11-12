import sys, json, base64, time

def read_json_line():
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError('Unexpected EOF while reading JSON line')
    return json.loads(line)

def query(forged_prev, target):
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    # send query JSON line
    print('{"q":"' + b64 + '"}')
    sys.stdout.flush()
    resp = read_json_line()
    return resp.get('pad_ok', False)

def recover_intermediate(prev_block, target_block, block_size=16):
    intermediate = bytearray(block_size)
    forged = bytearray(block_size)
    for idx in range(block_size-1, -1, -1):
        pad_val = block_size - idx
        # set bytes for already recovered positions
        for j in range(idx+1, block_size):
            forged[j] = intermediate[j] ^ pad_val
        found = None
        for guess in range(256):
            forged[idx] = guess
            if query(bytes(forged), target_block):
                found = guess
                break
        if found is None:
            raise RuntimeError(f'Failed to recover byte at index {idx}')
        intermediate[idx] = found ^ pad_val
    return bytes(intermediate)

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # read provisioned material from stdin (first line)
    prov = read_json_line()
    ct = bytes.fromhex(prov['ct_hex'])
    iv = bytes.fromhex(prov['iv_hex'])
    block_size = prov.get('block_size', 16)
    # split ciphertext into 16‑byte blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    start_ns = time.monotonic_ns()
    for i, target in enumerate(blocks):
        prev = iv if i == 0 else blocks[i-1]
        intermediate = recover_intermediate(prev, target, block_size)
        plain = xor_bytes(intermediate, prev)
        plaintext_blocks.append(plain)
    plaintext = b''.join(plaintext_blocks)
    duration = time.monotonic_ns() - start_ns
    claim = {"plaintext_hex": plaintext.hex()}
    print(f"OPSPAN_NS:{duration}")
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == '__main__':
    main()