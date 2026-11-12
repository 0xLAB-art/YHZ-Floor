import sys, json, base64, time

def read_response():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

def query(forged_prev, target):
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    print(json.dumps({"q": b64}), flush=True)
    resp = read_response()
    return resp.get('pad_ok', False)

def recover_intermediate(target, block_size=16):
    # recover Dk(target) (intermediate) using padding oracle
    I = bytearray(block_size)
    # work from last byte to first
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        # set bytes after pos to produce correct padding using known I
        prefix = bytearray(block_size)
        for j in range(pos+1, block_size):
            prefix[j] = I[j] ^ pad_val
        found = False
        for guess in range(256):
            forged = bytearray(prefix)
            forged[pos] = guess
            if query(forged, target):
                I[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            # In rare case of false negative, try again with different approach
            raise Exception('Failed to recover byte at position {}'.format(pos))
    return bytes(I)

def main():
    # provisioned data
    ct_hex = "c7711bdd7a8f67ed922f24fc47d82773a74ec4e22b956b8d136f111f9b06957d147c4a5c34b7a9915dcc9ed713761c0bf307d61ebc42f30fff02c6fc26db64f6ca9de52439ed691a16c07f0288c6f8cd"
    iv_hex = "09ea8825545288faceb05eef36757481"
    block_size = 16
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    # split ciphertext into blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext = bytearray()
    start = time.monotonic_ns()
    for idx, target in enumerate(blocks):
        prev = iv if idx == 0 else blocks[idx-1]
        intermediate = recover_intermediate(target, block_size)
        # plaintext block = intermediate XOR prev
        pblock = bytes(a ^ b for a, b in zip(intermediate, prev))
        plaintext.extend(pblock)
    end = time.monotonic_ns()
    # output claim (hex of plaintext, may include padding)
    print(f"CLAIM:{json.dumps({{'plaintext_hex': plaintext.hex()}})}")
    print(f"OPSPAN_NS:{end - start}")
    sys.stdout.flush()

if __name__ == '__main__':
    main()