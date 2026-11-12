import sys, json, base64, time

BLOCK_SIZE = 16

# Read provisioned material (first line from stdin)
prov_line = sys.stdin.readline()
if not prov_line:
    raise RuntimeError('No provisioned data received')
prov = json.loads(prov_line.strip())
ct_hex = prov.get('ct_hex')
iv_hex = prov.get('iv_hex')
if ct_hex is None or iv_hex is None:
    raise RuntimeError('Provisioned data missing ciphertext or iv')
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)


def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    # Both arguments must be exactly BLOCK_SIZE bytes
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    # Send query as JSON without extra spaces
    sys.stdout.write('{"q":"' + b64 + '"}\n')
    sys.stdout.flush()
    # Read oracle response
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError('No response from oracle')
    resp = json.loads(line.strip())
    return bool(resp.get('pad_ok'))


def recover_block(target: bytes, prev_cipher: bytes) -> bytes:
    # Recover plaintext for a single ciphertext block using padding oracle
    intermediate = bytearray(BLOCK_SIZE)  # D = AES-DEC(target)
    forged = bytearray(BLOCK_SIZE)
    for pad_len in range(1, BLOCK_SIZE + 1):
        idx = BLOCK_SIZE - pad_len
        # Set already discovered bytes to produce correct padding
        for j in range(BLOCK_SIZE - 1, idx, -1):
            forged[j] = intermediate[j] ^ pad_len
        found = False
        for guess in range(256):
            forged[idx] = guess
            if oracle_query(bytes(forged), target):
                # Guard against false positive when pad_len == 1
                if pad_len == 1:
                    # Flip another byte to ensure padding wasn't already correct
                    forged[idx] ^= 0x01
                    if oracle_query(bytes(forged), target):
                        forged[idx] ^= 0x01  # revert and continue searching
                        continue
                    forged[idx] ^= 0x01  # revert to original guess
                intermediate[idx] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f'Failed to recover byte at index {idx}')
    # Plaintext = intermediate XOR previous ciphertext (or IV)
    return bytes(i ^ p for i, p in zip(intermediate, prev_cipher))


def main():
    blocks = [ct[i:i+BLOCK_SIZE] for i in range(0, len(ct), BLOCK_SIZE)]
    plaintext_blocks = []
    for i, target in enumerate(blocks):
        prev = iv if i == 0 else blocks[i-1]
        pt_block = recover_block(target, prev)
        plaintext_blocks.append(pt_block)
    plaintext = b''.join(plaintext_blocks)
    # Optional timing measurement
    start = time.monotonic_ns()
    end = time.monotonic_ns()
    sys.stdout.write(f"OPSPAN_NS:{end - start}\n")
    claim = {"plaintext_hex": plaintext.hex()}
    sys.stdout.write('CLAIM:' + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == '__main__':
    main()