import sys, json, base64, time

def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    q = forged_prev + target
    assert len(q) == 32
    b64 = base64.b64encode(q).decode('ascii')
    sys.stdout.write('{"q": "' + b64 + '\"}\n')
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return False
    resp = json.loads(line)
    return bool(resp.get('pad_ok', False))

def decrypt_block(target: bytes, known: bytes) -> bytes:
    d = [0] * 16
    f = bytearray(16)
    for pos in range(15, -1, -1):
        pad_val = 16 - pos
        for j in range(pos + 1, 16):
            f[j] = d[j] ^ pad_val
        for guess in range(256):
            f[pos] = guess
            if oracle_query(bytes(f), target):
                d[pos] = f[pos] ^ pad_val
                break
        else:
            raise ValueError('Failed to find byte')
    return bytes(d)

def main():
    start = time.monotonic_ns()
    ct_hex = '7a21171fddef5b0afe8a7e5c408fd3720c3f33b3dfbbc6f92493e2a1f36309e4d6160e60e0b5b729ae2be4df9c18912b04658ca3fa65c1096206c5e634fe8c7c69d242fc8c4f218ac85440e17c66a323'
    iv_hex = 'cb68d605869a7b4a127cfac68b76fc2d'
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    prev = iv
    for target in reversed(blocks):
        d = decrypt_block(target, prev)
        p = bytes(d[i] ^ prev[i] for i in range(block_size))
        plaintext_blocks.append(p)
        prev = target
    plaintext_blocks.reverse()
    padded = b''.join(plaintext_blocks)
    pad_byte = padded[-1]
    if 1 <= pad_byte <= block_size:
        if padded[-pad_byte:] == bytes([pad_byte]) * pad_byte:
            unpadded = padded[:-pad_byte]
        else:
            unpadded = padded
    else:
        unpadded = padded
    plaintext_hex = unpadded.hex()
    end = time.monotonic_ns()
    sys.stdout.write(f'OPSPAN_NS:{end - start}\n')
    sys.stdout.write(f'CLAIM:{json.dumps({"plaintext_hex": plaintext_hex})}\n')
    sys.stdout.flush()

if __name__ == '__main__':
    main()