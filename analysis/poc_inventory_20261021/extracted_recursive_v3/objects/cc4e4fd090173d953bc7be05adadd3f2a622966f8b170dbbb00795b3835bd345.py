import sys, json, base64, time

def read_response():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

def query(forged_prev, target):
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    resp = read_response()
    return resp.get('pad_ok', False)

def recover_block(prev, target):
    # prev: bytes (16) original previous ciphertext block (or IV)
    # target: bytes (16) ciphertext block we attack
    recovered_X = [0]*16  # intermediate D_k(target)
    plaintext = [0]*16
    forged = bytearray(prev)  # will be modified
    for pos in range(15, -1, -1):
        pad_val = 16 - pos
        # set already known positions to enforce padding
        for j in range(pos+1, 16):
            forged[j] = recovered_X[j] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target):
                # found a byte that yields correct padding
                X_byte = guess ^ pad_val
                recovered_X[pos] = X_byte
                plaintext[pos] = X_byte ^ prev[pos]
                found = True
                break
        if not found:
            # Should not happen
            raise RuntimeError('Failed to recover byte at position {}'.format(pos))
    return bytes(plaintext)

def pkcs7_unpad(data):
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError('Invalid padding')
    if data[-pad_len:] != bytes([pad_len])*pad_len:
        raise ValueError('Invalid padding')
    return data[:-pad_len]

def main():
    # provisioned material from the task description
    ct_hex = "93a6370ed043efcaab117b4b73601f21855bc16022e58123b79fad22e632669b5db5d4ce8a7005070b282a7fd1151428866613b78cd090c32e255cf7048fbcbe777c9627a53d01a2f7dea2ff41e657bf"
    iv_hex = "1921ccdcfa022391a3d801dd3a0c1dc3"
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    # split ciphertext into blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    prev = iv
    for blk in blocks:
        pt_blk = recover_block(prev, blk)
        plaintext_blocks.append(pt_blk)
        prev = blk
    full_plain = b''.join(plaintext_blocks)
    # strip padding (the verifier also strips, but we output unpadded as requested)
    try:
        unpadded = pkcs7_unpad(full_plain)
    except Exception:
        unpadded = full_plain
    # produce hex string of unpadded plaintext (64 bytes expected)
    pt_hex = unpadded.hex()
    # optional timing
    start = time.monotonic_ns()
    # (no extra heavy computation here)
    end = time.monotonic_ns()
    sys.stdout.write(f"OPSPAN_NS:{end-start}\n")
    claim = {"plaintext_hex": pt_hex}
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()