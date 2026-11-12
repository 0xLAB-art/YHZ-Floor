import sys, json, base64, time

def read_response():
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)
    return json.loads(line)

def query(forged_prev, target):
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    print(json.dumps({"q": b64}))
    sys.stdout.flush()
    resp = read_response()
    return resp.get('pad_ok', False)

def recover_intermediate(prev_block, target_block, block_size=16):
    # returns D_k(target_block) as bytes
    intermediate = bytearray(block_size)
    forged = bytearray(block_size)
    for idx in range(block_size-1, -1, -1):
        pad_val = block_size - idx
        # set already discovered bytes to produce correct padding
        for j in range(idx+1, block_size):
            forged[j] = intermediate[j] ^ pad_val
        found = None
        for guess in range(256):
            forged[idx] = guess
            if query(bytes(forged), target_block):
                found = guess
                break
        if found is None:
            raise RuntimeError('Failed to recover byte at position {}'.format(idx))
        intermediate[idx] = found ^ pad_val
    return bytes(intermediate)

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def main():
    # provisioned material (hard‑coded as per task description)
    prov = {
        "ct_hex": "047cd2c42056d3a8a4ecff7f7dee7c668e3748af322eed91e42ee481b884791a72746814aebdb6d3085dc17c74c19be6cea8257fd6bd5f90790ede23cc62ccac19dfdb35c78506c2868a7cfcaa428d0f",
        "iv_hex": "489201d1362d6114886e60170a98eb62"
    }
    ct = bytes.fromhex(prov["ct_hex"])
    iv = bytes.fromhex(prov["iv_hex"])
    block_size = 16
    # split ciphertext into blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    start_ns = time.monotonic_ns()
    for i, target in enumerate(blocks):
        prev = iv if i == 0 else blocks[i-1]
        intermediate = recover_intermediate(prev, target, block_size)
        plain = xor_bytes(intermediate, prev)
        plaintext_blocks.append(plain)
    plaintext = b''.join(plaintext_blocks)
    # output claim (hex of full padded plaintext)
    claim = {"plaintext_hex": plaintext.hex()}
    end_ns = time.monotonic_ns()
    print(f"OPSPAN_NS:{end_ns - start_ns}")
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()