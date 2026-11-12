import sys, json, base64, time

def read_provision():
    # Provisioned material is embedded in the task description.
    ct_hex = "c2fdd5bba0f0f34b3b12f7d55df98c02658eb764338d0c2cbaf7580a645468dc34b8e459e70ca5209b7a6bf4fcd23a2364e9f9f524635518b19ef94990ffae77bfb481c845c32d2ad155cdad959cce28"
    iv_hex = "fd2a7e8ad91248a35cef91621d184830"
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    # split ciphertext into 16-byte blocks
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    return iv, blocks

def query(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)
    resp = json.loads(line)
    return resp.get("pad_ok", False)

def recover_intermediate(target_block: bytes, prev_block: bytes) -> bytes:
    # classic padding oracle attack to recover D(target_block)
    block_size = 16
    intermediate = bytearray(block_size)
    forged = bytearray(block_size)
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        # set bytes after pos to enforce correct padding
        for i in range(pos+1, block_size):
            forged[i] = intermediate[i] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess
            # other earlier bytes can be zero (already zero)
            if query(bytes(forged), target_block):
                # recover intermediate byte
                intermediate[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            # should not happen
            raise RuntimeError("Failed to recover byte at position {}".format(pos))
    return bytes(intermediate)

def pkcs7_unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding")
    if data[-pad_len:] != bytes([pad_len])*pad_len:
        raise ValueError("Invalid padding")
    return data[:-pad_len]

def main():
    start = time.monotonic_ns()
    iv, blocks = read_provision()
    plaintext_blocks = []
    prev = iv
    for idx, block in enumerate(blocks):
        intermediate = recover_intermediate(block, prev)
        # plaintext = intermediate XOR prev
        pt = bytes(a ^ b for a, b in zip(intermediate, prev))
        plaintext_blocks.append(pt)
        prev = block
    padded_plaintext = b"".join(plaintext_blocks)
    try:
        plaintext = pkcs7_unpad(padded_plaintext)
    except Exception:
        plaintext = padded_plaintext  # fallback, verifier will strip if needed
    duration = time.monotonic_ns() - start
    # output optional timing
    sys.stdout.write(f"OPSPAN_NS:{duration}\n")
    sys.stdout.flush()
    claim = {"plaintext_hex": plaintext.hex()}
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()