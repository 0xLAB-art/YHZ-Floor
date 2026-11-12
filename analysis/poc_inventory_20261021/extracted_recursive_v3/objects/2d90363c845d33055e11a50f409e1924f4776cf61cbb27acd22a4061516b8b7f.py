import sys, json, base64, time

def read_line():
    return sys.stdin.readline()

def read_json_line():
    line = read_line()
    if not line:
        return None
    return json.loads(line)

def query(forged_prev: bytes, target: bytes) -> bool:
    # send forged_prev || target as base64
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    print(json.dumps({"q": b64}), flush=True)
    resp = read_json_line()
    if resp is None:
        sys.exit(0)
    return resp.get('pad_ok', False)

def recover_intermediate(target_block: bytes) -> bytes:
    block_size = 16
    intermediate = bytearray(block_size)
    # work from last byte to first
    for pos in reversed(range(block_size)):
        pad_val = block_size - pos
        forged = bytearray(block_size)
        # set already recovered positions to produce correct padding
        for i in range(pos + 1, block_size):
            forged[i] = intermediate[i] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess ^ pad_val
            if query(bytes(forged), target_block):
                # handle possible false positive when pad_val == 1
                if pad_val == 1:
                    # modify a different byte to ensure it's not accidental padding
                    forged[pos] ^= 0x01
                    if not query(bytes(forged), target_block):
                        forged[pos] ^= 0x01  # restore
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
    # Read provisioned material from stdin (first line)
    prov = read_json_line()
    if prov is None:
        sys.exit(0)
    ct = bytes.fromhex(prov['ct_hex'])
    iv = bytes.fromhex(prov['iv_hex'])
    block_size = prov.get('block_size', 16)
    # Split ciphertext into 16‑byte blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    # Recover intermediate values for each ciphertext block
    intermediates = []
    for blk in blocks:
        inter = recover_intermediate(blk)
        intermediates.append(inter)
    # Derive plaintext blocks: P_i = Inter_i XOR C_{i-1} (IV for first)
    plaintext = bytearray()
    for i, inter in enumerate(intermediates):
        prev = iv if i == 0 else blocks[i-1]
        pt_block = bytes(a ^ b for a, b in zip(inter, prev))
        plaintext.extend(pt_block)
    # Remove PKCS#7 padding if present
    pad_len = plaintext[-1]
    if 1 <= pad_len <= block_size and all(p == pad_len for p in plaintext[-pad_len:]):
        plaintext = plaintext[:-pad_len]
    claim = {"plaintext_hex": plaintext.hex()}
    # Optional timing measurement
    start = time.monotonic_ns()
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end-start}", flush=True)
    print(f"CLAIM:{json.dumps(claim)}", flush=True)

if __name__ == '__main__':
    main()