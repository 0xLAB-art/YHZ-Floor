import sys, json, base64, time

def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    # forged_prev and target are each 16 bytes
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError("No response from oracle")
    resp = json.loads(line)
    return bool(resp.get("pad_ok"))

def recover_block(target: bytes, original_prev: bytes) -> bytes:
    # Returns plaintext block (16 bytes) = D xor original_prev
    block_size = 16
    intermediate = bytearray(block_size)  # D = AES-DEC(target)
    forged = bytearray(block_size)
    # iterate from last byte to first
    for pad_len in range(1, block_size + 1):
        idx = block_size - pad_len
        # set bytes after idx to produce correct padding
        for j in range(block_size - 1, idx, -1):
            forged[j] = intermediate[j] ^ pad_len
        # try all possible byte values for position idx
        found = False
        for guess in range(256):
            forged[idx] = guess
            # other untouched bytes (0..idx-1) can be anything; keep as 0
            if oracle_query(bytes(forged), target):
                # deduce intermediate byte
                intermediate[idx] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError("Failed to recover byte at position {}".format(idx))
    # plaintext = intermediate xor original_prev
    plaintext = bytes(i ^ o for i, o in zip(intermediate, original_prev))
    return plaintext

def main():
    ct_hex = "d84ee5701baeea30ef2e0fb3937bd8b336a691d560467eb57a957ba73bc6318f12c811e24e44c70b2793ab6f2ce5d31154db687fadb9626e0f695fd39632454ec47f75faa4ea66315f85216c6e8dc21a"
    iv_hex = "df19ae40f7f575631c6260f4e22d7f01"
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    # split ciphertext into blocks
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    for i, target in enumerate(blocks):
        prev = iv if i == 0 else blocks[i-1]
        pt_block = recover_block(target, prev)
        plaintext_blocks.append(pt_block)
    plaintext = b"".join(plaintext_blocks)
    # optional timing measurement
    start = time.monotonic_ns()
    # (no extra heavy work)
    end = time.monotonic_ns()
    sys.stdout.write(f"OPSPAN_NS:{end - start}\n")
    sys.stdout.flush()
    claim = {"plaintext_hex": plaintext.hex()}
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()