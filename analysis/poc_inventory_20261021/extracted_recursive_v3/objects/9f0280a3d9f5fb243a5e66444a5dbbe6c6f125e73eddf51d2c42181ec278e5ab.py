import sys, base64, json, time

BLOCK_SIZE = 16

def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    # forged_prev and target are each exactly BLOCK_SIZE bytes
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    # protocol requires compact JSON without spaces
    sys.stdout.write('{"q":"' + b64 + '"}\n')
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError('No response from oracle')
    resp = json.loads(line.strip())
    return bool(resp.get('pad_ok'))

def recover_block(target: bytes, prev_cipher: bytes) -> bytes:
    # Recover plaintext block for given target ciphertext block and its preceding ciphertext (or IV)
    intermediate = bytearray(BLOCK_SIZE)  # D = AES-DEC(target)
    forged = bytearray(BLOCK_SIZE)
    # iterate padding length from 1 to BLOCK_SIZE
    for pad_len in range(1, BLOCK_SIZE + 1):
        idx = BLOCK_SIZE - pad_len
        # set already discovered positions to produce correct padding
        for j in range(BLOCK_SIZE - 1, idx, -1):
            forged[j] = intermediate[j] ^ pad_len
        # try all possible byte values for current position
        found = False
        for guess in range(256):
            forged[idx] = guess
            # other bytes (0..idx-1) can stay as 0
            if oracle_query(bytes(forged), target):
                # handle the special case where padding_len == 1 and the guess happens to be the original byte
                # In that case the oracle may return true for the original padding; we verify by changing another byte
                if pad_len == 1:
                    # flip a different byte to ensure it's not a false positive
                    forged[idx] = guess ^ 0x01
                    if not oracle_query(bytes(forged), target):
                        # original guess was correct
                        forged[idx] = guess
                    else:
                        # false positive, continue searching
                        forged[idx] = guess
                        continue
                intermediate[idx] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f'Failed to recover byte at index {idx}')
    # plaintext = intermediate XOR previous ciphertext (or IV)
    return bytes(i ^ p for i, p in zip(intermediate, prev_cipher))

def main():
    ct_hex = "d84ee5701baeea30ef2e0fb3937bd8b336a691d560467eb57a957ba73bc6318f12c811e24e44c70b2793ab6f2ce5d31154db687fadb9626e0f695fd39632454ec47f75faa4ea66315f85216c6e8dc21a"
    iv_hex = "df19ae40f7f575631c6260f4e22d7f01"
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    blocks = [ct[i:i+BLOCK_SIZE] for i in range(0, len(ct), BLOCK_SIZE)]
    plaintext_blocks = []
    for i, target in enumerate(blocks):
        prev = iv if i == 0 else blocks[i-1]
        pt = recover_block(target, prev)
        plaintext_blocks.append(pt)
    plaintext = b''.join(plaintext_blocks)
    # optional timing measurement
    start = time.monotonic_ns()
    end = time.monotonic_ns()
    sys.stdout.write(f"OPSPAN_NS:{end - start}\n")
    claim = {"plaintext_hex": plaintext.hex()}
    sys.stdout.write('CLAIM:' + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == '__main__':
    main()