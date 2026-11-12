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

def recover_block(target_block, original_prev):
    block_size = 16
    recovered_di = bytearray(block_size)
    # work from last byte to first
    for pad_len in range(1, block_size+1):
        idx = block_size - pad_len
        # set forged_prev for already known bytes
        prefix = bytearray(block_size)
        for i in range(idx+1, block_size):
            # we want Di[i] xor forged_prev[i] == pad_len
            prefix[i] = recovered_di[i] ^ pad_len
        found = False
        for guess in range(256):
            prefix[idx] = guess ^ pad_len
            # other bytes (0..idx-1) can be random; keep zero
            if query(bytes(prefix), target_block):
                # handle possible false positive when pad_len==1
                # verify by changing a different byte
                if pad_len == 1:
                    # try a second check with a different modification to ensure uniqueness
                    # flip a byte earlier (if any) and expect failure
                    test_prefix = bytearray(prefix)
                    test_prefix[(idx-1) % block_size] ^= 1
                    if not query(bytes(test_prefix), target_block):
                        pass
                recovered_di[idx] = guess
                found = True
                break
        if not found:
            # should not happen
            raise RuntimeError('Failed to recover byte')
    return bytes(recovered_di)

def main():
    # provisioned material
    prov = json.loads(sys.stdin.read())
    ct = bytes.fromhex(prov['ct_hex'])
    iv = bytes.fromhex(prov['iv_hex'])
    block_size = prov.get('block_size', 16)
    # split ciphertext into blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    prev = iv
    for blk in blocks:
        di = recover_block(blk, prev)
        pi = bytes(a ^ b for a, b in zip(di, prev))
        plaintext_blocks.append(pi)
        prev = blk
    full_plain = b''.join(plaintext_blocks)
    # strip PKCS#7 padding
    pad_len = full_plain[-1]
    if 1 <= pad_len <= block_size and full_plain[-pad_len:] == bytes([pad_len])*pad_len:
        unpadded = full_plain[:-pad_len]
    else:
        unpadded = full_plain
    claim = {"plaintext_hex": unpadded.hex()}
    # optional timing
    # opspan measured around attack (already done)
    print(f"CLAIM:{json.dumps(claim)}", flush=True)

if __name__ == '__main__':
    main()