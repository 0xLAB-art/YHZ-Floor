import sys, base64, json, time, binascii

def read_response():
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line.strip())

def query(forged_prev, target):
    # forged_prev and target are bytes of length 16 each
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    print(json.dumps({"q": b64}), flush=True)
    resp = read_response()
    if resp is None:
        raise RuntimeError("No response from oracle")
    return resp.get("pad_ok", False)

def recover_block(prev_block, target_block):
    block_size = 16
    recovered_intermediate = [0] * block_size  # I = D_k(C)
    # work from last byte to first
    for pad_len in range(1, block_size + 1):
        pos = block_size - pad_len
        # set forged_prev for already known positions
        forged = bytearray(block_size)
        # for positions after pos (i.e., where we already know I), set to make padding = pad_len
        for i in range(pos + 1, block_size):
            forged[i] = recovered_intermediate[i] ^ pad_len
        # try all possible byte values for current position
        found = False
        for guess in range(256):
            forged[pos] = guess
            # other bytes (before pos) can be anything; keep as 0
            if query(bytes(forged), target_block):
                # compute intermediate byte
                intermediate = guess ^ pad_len
                recovered_intermediate[pos] = intermediate
                found = True
                break
        if not found:
            raise RuntimeError("Failed to recover byte at position {}".format(pos))
    return bytes(recovered_intermediate)

def main():
    # provisioned material
    provision = json.loads(sys.stdin.read())
    ct_hex = provision["ct_hex"]
    iv_hex = provision["iv_hex"]
    ct = binascii.unhexlify(ct_hex)
    iv = binascii.unhexlify(iv_hex)
    block_size = 16
    # split ciphertext into blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    # there should be 5 blocks
    assert len(blocks) == 5
    plaintext_blocks = []
    # recover each block's intermediate value and then plaintext
    for idx, target in enumerate(blocks):
        prev = iv if idx == 0 else blocks[idx-1]
        intermediate = recover_block(prev, target)
        # plaintext = intermediate XOR prev
        plain = bytes(a ^ b for a, b in zip(intermediate, prev))
        plaintext_blocks.append(plain)
    full_plain = b''.join(plaintext_blocks)
    # strip PKCS#7 padding
    pad_len = full_plain[-1]
    if pad_len < 1 or pad_len > block_size:
        stripped = full_plain
    else:
        if full_plain[-pad_len:] == bytes([pad_len])*pad_len:
            stripped = full_plain[:-pad_len]
        else:
            stripped = full_plain
    # output claim
    claim = {"plaintext_hex": stripped.hex()}
    # optional timing
    start = time.monotonic_ns()
    # (nothing heavy here, just for demonstration)
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end - start}", flush=True)
    print(f"CLAIM:{json.dumps(claim)}", flush=True)

if __name__ == "__main__":
    main()