import sys, json, base64, time

# Padding oracle query: send forged_prev || target (both 16 bytes) as base64
def query(forged_prev: bytes, target: bytes) -> bool:
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode()
    print(json.dumps({"q": b64}, separators=(',', ':')), flush=True)
    # read oracle response (a single JSON line)
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    resp = json.loads(line)
    return resp.get('pad_ok', False)

# Recover one plaintext block given its ciphertext block (target) and the preceding ciphertext block (prev)
def recover_block(target: bytes, prev: bytes) -> bytes:
    bs = 16
    intermediate = [0] * bs  # D_k(target)
    forged = bytearray(bs)
    for pos in range(bs - 1, -1, -1):
        pad_val = bs - pos
        # set bytes after pos to enforce correct padding
        for j in range(pos + 1, bs):
            forged[j] = prev[j] ^ intermediate[j] ^ pad_val
        found = False
        for guess in range(256):
            # guess is the intermediate byte value
            forged[pos] = prev[pos] ^ guess ^ pad_val
            if query(bytes(forged), target):
                # When pad_val == 1, a false positive can happen (original padding 0x01).
                # Verify by flipping another byte.
                if pad_val == 1:
                    forged[pos] ^= 1
                    if not query(bytes(forged), target):
                        forged[pos] ^= 1
                        intermediate[pos] = guess ^ pad_val
                        found = True
                        break
                    forged[pos] ^= 1
                intermediate[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at position {pos}")
    # plaintext = intermediate XOR prev
    return bytes(i ^ p for i, p in zip(intermediate, prev))


def main():
    # Provisioned material (hard‑coded from the task description)
    ct_hex = "4da13dfa23b340d64743476bda799dfafd37b7090f503698b796976faadc74e02d6e8a589fabb9e460ec83d99c5bd311ef4795b29c305d3ae0c075e70643f0fb72b2b5fee21dd4279c95184cddb1a443"
    iv_hex = "b77356ac6815e29b39a40ec792042ee3"
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    # Split ciphertext into 16‑byte blocks
    blocks = [iv] + [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    start = time.monotonic_ns()
    for i in range(1, len(blocks)):
        pt_block = recover_block(blocks[i], blocks[i-1])
        plaintext_blocks.append(pt_block)
    plaintext = b''.join(plaintext_blocks)
    end = time.monotonic_ns()
    # Optional timing output
    print(f"OPSPAN_NS:{end-start}", flush=True)
    claim = {"plaintext_hex": plaintext.hex()}
    print('CLAIM:' + json.dumps(claim, separators=(',', ':')), flush=True)

if __name__ == '__main__':
    main()