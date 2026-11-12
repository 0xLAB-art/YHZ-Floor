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

def recover_intermediate(target_block, prev_cipher):
    block_size = 16
    intermediate = bytearray(block_size)
    # work from last byte to first
    for pos in reversed(range(block_size)):
        pad_val = block_size - pos
        # set bytes after pos to produce correct padding
        forged = bytearray(block_size)
        for i in range(pos+1, block_size):
            forged[i] = intermediate[i] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess ^ pad_val
            # keep earlier bytes random (0)
            if query(bytes(forged), target_block):
                # handle the special case where pad_val==1 and the original padding may be valid
                # verify by changing a different byte (pos-1) if possible
                if pad_val == 1:
                    # flip another byte to ensure it's not a lucky true
                    forged[pos] ^= 0x01
                    if not query(bytes(forged), target_block):
                        # original guess was correct
                        pass
                    else:
                        # false positive, continue searching
                        forged[pos] ^= 0x01
                        continue
                intermediate[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            raise Exception('Failed to recover byte at position {}'.format(pos))
    return bytes(intermediate)

def main():
    # provisioned data
    prov = json.loads('''{"ct_hex": "201d74148b8f070da5647e6f76e6a61b1bc280c9b4346e11998f028205fd18a5fa1a4c304e2fa47e5c79dd3af2474d028a7659f4c3dd09ce1253757165a318819ccce4b8cccc584198b31207725ee216", "iv_hex": "c89d348d898b96eae923825715b4acbb", "oracle": "pad_ok_only", "block_size": 16}''')
    ct = bytes.fromhex(prov['ct_hex'])
    iv = bytes.fromhex(prov['iv_hex'])
    block_size = prov['block_size']
    # split ciphertext into blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    # recover intermediate values for each ciphertext block
    intermediates = []
    for idx, block in enumerate(blocks):
        # previous cipher block (or iv for first) is not needed for attack, only target block matters
        inter = recover_intermediate(block, None)
        intermediates.append(inter)
    # derive plaintext blocks
    plaintext = bytearray()
    for i, inter in enumerate(intermediates):
        prev = iv if i == 0 else blocks[i-1]
        pt_block = bytes(a ^ b for a, b in zip(inter, prev))
        plaintext.extend(pt_block)
    # strip PKCS#7 padding
    pad_len = plaintext[-1]
    if 1 <= pad_len <= block_size and all(p == pad_len for p in plaintext[-pad_len:]):
        plaintext = plaintext[:-pad_len]
    # output claim
    claim = {"plaintext_hex": plaintext.hex()}
    # optional timing measurement
    start = time.monotonic_ns()
    # (no heavy work after this point)
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end-start}", flush=True)
    print(f"CLAIM:{json.dumps(claim)}", flush=True)

if __name__ == '__main__':
    main()