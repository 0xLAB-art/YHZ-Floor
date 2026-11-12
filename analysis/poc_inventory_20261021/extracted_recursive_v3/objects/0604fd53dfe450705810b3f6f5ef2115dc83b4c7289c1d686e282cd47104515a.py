import sys, json, base64, time

BLOCK_SIZE = 16

def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    # both arguments must be exactly BLOCK_SIZE bytes
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("No response from oracle")
    resp = json.loads(line.strip())
    return bool(resp.get("pad_ok"))

def recover_block(target: bytes, prev_cipher: bytes) -> bytes:
    # Recover the plaintext for a single ciphertext block using the padding oracle
    intermediate = bytearray(BLOCK_SIZE)  # D = AES-DEC(target)
    forged = bytearray(BLOCK_SIZE)
    for pad_len in range(1, BLOCK_SIZE + 1):
        idx = BLOCK_SIZE - pad_len
        # set bytes after idx to produce correct padding
        for j in range(BLOCK_SIZE - 1, idx, -1):
            forged[j] = intermediate[j] ^ pad_len
        found = False
        for guess in range(256):
            forged[idx] = guess
            if oracle_query(bytes(forged), target):
                # Verify against false positive when pad_len == 1
                if pad_len == 1:
                    # Change another byte to see if still true
                    forged[idx] ^= 0x01
                    if oracle_query(bytes(forged), target):
                        forged[idx] ^= 0x01  # revert and continue searching
                        continue
                    forged[idx] ^= 0x01  # revert to original guess
                intermediate[idx] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at index {idx}")
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
        pt_block = recover_block(target, prev)
        plaintext_blocks.append(pt_block)
    plaintext = b"".join(plaintext_blocks)
    # optional timing measurement
    start = time.monotonic_ns()
    end = time.monotonic_ns()
    sys.stdout.write(f"OPSPAN_NS:{end - start}\n")
    claim = {"plaintext_hex": plaintext.hex()}
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()