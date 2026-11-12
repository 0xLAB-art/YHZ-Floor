import sys, json, base64, time

def read_response():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

def send_query(data_bytes):
    b64 = base64.b64encode(data_bytes).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    resp = read_response()
    return resp.get("pad_ok", False)

def main():
    # provisioned material (hard‑coded as given in the task description)
    ct_hex = "48c20f297c8a30157899501eeb94bf5decd7ff78ea9d92a347e3c4d4042d2abcbd8d90580551bd31a0b1763cc94946f1cd7172dca4df476d4101a230bdb1683f303d28cc62782f3b323b79f9fca28586"
    iv_hex = "a32f1639127c714e024af7f53a08baaa"
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    # split ciphertext into blocks
    blocks = [iv]
    for i in range(0, len(ct), block_size):
        blocks.append(ct[i:i+block_size])
    n_blocks = len(blocks) - 1  # number of ciphertext blocks (excluding IV)
    plaintext_blocks = []
    # recover each block independently, starting from the first ciphertext block
    for block_index in range(1, n_blocks+1):
        C_i = blocks[block_index]
        C_prev = blocks[block_index-1]
        recovered = bytearray(block_size)
        forged = bytearray(block_size)
        # attack byte by byte from the end of the block
        for pos in range(block_size-1, -1, -1):
            pad_val = block_size - pos
            # set bytes after pos to enforce correct padding
            for j in range(block_size-1, pos, -1):
                forged[j] = recovered[j] ^ pad_val
            # try all possible byte values for the current position
            found = False
            for guess in range(256):
                forged[pos] = guess
                query = bytes(forged) + C_i
                if send_query(query):
                    # valid padding -> recover plaintext byte
                    recovered[pos] = guess ^ pad_val
                    found = True
                    break
            if not found:
                # Should not happen; but to avoid infinite loops, abort
                sys.stderr.write(f"Failed to recover byte at block {block_index}, pos {pos}\n")
                sys.exit(1)
        # after full block recovered, compute actual plaintext block by XOR with original previous ciphertext block
        plain_block = bytes(p ^ c for p, c in zip(recovered, C_prev))
        plaintext_blocks.append(plain_block)
    plaintext = b"".join(plaintext_blocks)
    # output claim
    start = time.monotonic_ns()
    # (no extra computation after start, just measuring)
    end = time.monotonic_ns()
    sys.stdout.write(f"OPSPAN_NS:{end-start}\n")
    claim = {"plaintext_hex": plaintext.hex()}
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()