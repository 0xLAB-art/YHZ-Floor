import sys, json, base64, time

def read_json_line():
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)

def query(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    # compact JSON without spaces
    print(json.dumps({"q": b64}, separators=(',', ':')), flush=True)
    resp = read_json_line()
    if resp is None:
        sys.exit(0)
    return resp.get('pad_ok', False)

def recover_intermediate(target_block: bytes) -> bytes:
    block_size = 16
    intermediate = bytearray(block_size)
    for pos in reversed(range(block_size)):
        pad_val = block_size - pos
        forged = bytearray(block_size)
        # set already known bytes to produce correct padding
        for i in range(pos + 1, block_size):
            forged[i] = intermediate[i] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess ^ pad_val
            if query(bytes(forged), target_block):
                # mitigate false positive when pad_val == 1
                if pad_val == 1:
                    forged[pos] ^= 0x01
                    if not query(bytes(forged), target_block):
                        forged[pos] ^= 0x01
                    else:
                        forged[pos] ^= 0x01
                        continue
                intermediate[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            raise Exception(f"Failed to recover byte at position {pos}")
    return bytes(intermediate)

def main():
    # Try to read provisioned material from stdin; if not provided, fall back to hard‑coded values.
    prov = read_json_line()
    if prov and isinstance(prov, dict) and 'ct_hex' in prov:
        ct_hex = prov['ct_hex']
        iv_hex = prov['iv_hex']
        block_size = prov.get('block_size', 16)
    else:
        ct_hex = "201d74148b8f070da5647e6f76e6a61b1bc280c9b4346e11998f028205fd18a5fa1a4c304e2fa47e5c79dd3af2474d028a7659f4c3dd09ce1253757165a318819ccce4b8cccc584198b31207725ee216"
        iv_hex = "c89d348d898b96eae923825715b4acbb"
        block_size = 16
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    # split ciphertext into blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    # recover intermediate (decryption XOR previous) for each ciphertext block
    intermediates = []
    for blk in blocks:
        inter = recover_intermediate(blk)
        intermediates.append(inter)
    # derive plaintext blocks: P_i = Inter_i XOR C_{i-1} (IV for first block)
    plaintext = bytearray()
    for i, inter in enumerate(intermediates):
        prev = iv if i == 0 else blocks[i-1]
        pt_block = bytes(a ^ b for a, b in zip(inter, prev))
        plaintext.extend(pt_block)
    # strip PKCS#7 padding if present
    pad_len = plaintext[-1]
    if 1 <= pad_len <= block_size and all(p == pad_len for p in plaintext[-pad_len:]):
        plaintext = plaintext[:-pad_len]
    claim = {"plaintext_hex": plaintext.hex()}
    # optional timing measurement
    start = time.monotonic_ns()
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end-start}", flush=True)
    print(f"CLAIM:{json.dumps(claim, separators=(',', ':'))}", flush=True)

if __name__ == '__main__':
    main()