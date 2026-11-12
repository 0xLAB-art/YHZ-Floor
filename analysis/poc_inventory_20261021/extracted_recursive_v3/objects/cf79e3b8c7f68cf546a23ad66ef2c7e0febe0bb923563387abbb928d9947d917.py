import sys, json, base64, time

def read_line():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return line.rstrip('\n')

def read_response():
    resp_line = read_line()
    return json.loads(resp_line)

def send_query(data_bytes):
    b64 = base64.b64encode(data_bytes).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    resp = read_response()
    return resp.get("pad_ok", False)

def main():
    # Read provisioned material from stdin (first line)
    prov_line = read_line()
    prov = json.loads(prov_line)
    ct = bytes.fromhex(prov["ct_hex"])
    iv = bytes.fromhex(prov["iv_hex"])
    block_size = prov.get("block_size", 16)
    # Split ciphertext into blocks, prepend IV as block 0
    blocks = [iv]
    for i in range(0, len(ct), block_size):
        blocks.append(ct[i:i+block_size])
    n_blocks = len(blocks) - 1
    plaintext_blocks = []
    # Recover each ciphertext block
    for block_index in range(1, n_blocks + 1):
        C_i = blocks[block_index]
        C_prev = blocks[block_index - 1]
        recovered = bytearray(block_size)
        forged = bytearray(block_size)
        for pos in range(block_size - 1, -1, -1):
            pad_val = block_size - pos
            # set padding for already recovered bytes
            for j in range(block_size - 1, pos, -1):
                forged[j] = recovered[j] ^ pad_val
            # try all possible byte values
            found = False
            for guess in range(256):
                forged[pos] = guess
                query = bytes(forged) + C_i
                if send_query(query):
                    recovered[pos] = guess ^ pad_val
                    found = True
                    break
            if not found:
                # If not found, something went wrong; abort
                sys.stderr.write(f"Failed to recover byte at block {block_index}, pos {pos}\n")
                sys.exit(1)
        # Derive plaintext block by XOR with original previous ciphertext block
        plain_block = bytes(p ^ c for p, c in zip(recovered, C_prev))
        plaintext_blocks.append(plain_block)
    plaintext = b"".join(plaintext_blocks)
    # Output claim
    start = time.monotonic_ns()
    # (no extra work)
    end = time.monotonic_ns()
    sys.stdout.write(f"OPSPAN_NS:{end - start}\n")
    claim = {"plaintext_hex": plaintext.hex()}
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()