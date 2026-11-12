import sys, json, base64, time

def read_response():
    while True:
        line = sys.stdin.readline()
        if not line:
            continue
        line = line.strip()
        if line:
            try:
                return json.loads(line)
            except Exception:
                continue

def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    # concatenate forged_prev || target, base64 encode
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    print(json.dumps({"q": b64}))
    sys.stdout.flush()
    resp = read_response()
    return bool(resp.get('pad_ok'))

def recover_block(prev_block: bytes, target_block: bytes) -> bytes:
    block_size = len(prev_block)
    intermediate = bytearray(block_size)
    forged = bytearray(block_size)
    # work from last byte to first
    for pos in range(block_size-1, -1, -1):
        pad_len = block_size - pos
        # set known bytes for padding
        for i in range(pos+1, block_size):
            forged[i] = intermediate[i] ^ pad_len
        # For the last byte (pos == block_size-1) we need to avoid false positive due to original padding
        start_guess = 0
        if pos == block_size-1:
            # flip a different byte to ensure padding invalid initially
            forged[pos-1] ^= 0x01
        found = False
        for guess in range(256):
            forged[pos] = guess
            if oracle_query(bytes(forged), target_block):
                # possible candidate
                intermediate[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            raise Exception('Failed to recover byte at position {}'.format(pos))
        if pos == block_size-1:
            # revert the byte we flipped earlier
            forged[pos-1] ^= 0x01
    return bytes(intermediate)

def main():
    # provisioned data
    prov = json.loads('''{"ct_hex": "770e8db86bdff1f899bb9bcdddbff33d81d6961f137f0e7526d49e41ae5d51959768eb08c595be7b874c4a4e37b24565062c30a5c8980440c67761f261809f4dd5e5195c68e44ec5051eddc84a5bebbb", "iv_hex": "bc825c3cd7fd7c756223263d54d74824", "oracle": "pad_ok_only", "block_size": 16}''')
    ct = bytes.fromhex(prov['ct_hex'])
    iv = bytes.fromhex(prov['iv_hex'])
    block_size = prov['block_size']
    # split ciphertext into blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext = bytearray()
    prev = iv
    for blk in blocks:
        intermediate = recover_block(prev, blk)
        plain_block = bytes(a ^ b for a, b in zip(intermediate, prev))
        plaintext.extend(plain_block)
        prev = blk
    # remove PKCS#7 padding
    pad_len = plaintext[-1]
    if pad_len < 1 or pad_len > block_size:
        unpadded = bytes(plaintext)
    else:
        unpadded = bytes(plaintext[:-pad_len])
    # claim
    claim = {"plaintext_hex": unpadded.hex()}
    # optional timing
    # start = time.monotonic_ns()
    # end = time.monotonic_ns()
    # print(f"OPSPAN_NS:{end-start}")
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()