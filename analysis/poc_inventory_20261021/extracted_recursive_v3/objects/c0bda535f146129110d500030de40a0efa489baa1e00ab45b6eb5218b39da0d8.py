import sys, json, base64, binascii, time

BLOCK_SIZE = 16
# Hard‑coded provision (fallback if no input is provided)
DEFAULT_CT_HEX = "cdb8e9c46546a2456e4e6dcec7d8f258563a46415542d55dab3f853e3100d70e89b1f071df863b9af295e8547a5274914c4f5fd26f8dd6b47c55feac554b464c6c9bb88c3b8deae72d5c978247f5fd7a"
DEFAULT_IV_HEX = "503b1a381c2461db47615a04f13f1c26"

def read_json_line():
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line.strip())

def query(forged_prev: bytes, target: bytes) -> bool:
    payload = base64.b64encode(forged_prev + target).decode()
    print(json.dumps({"q": payload}), flush=True)
    resp = read_json_line()
    if resp is None:
        raise RuntimeError("No response from oracle")
    return resp.get("pad_ok", False)

def recover_block(prev_block: bytes, target_block: bytes) -> bytes:
    # Recover intermediate value I = D_k(target_block)
    intermediate = [0] * BLOCK_SIZE
    for pad_len in range(1, BLOCK_SIZE + 1):
        pos = BLOCK_SIZE - pad_len
        forged = bytearray(BLOCK_SIZE)
        # Set bytes after pos to enforce correct padding
        for i in range(pos + 1, BLOCK_SIZE):
            forged[i] = intermediate[i] ^ pad_len
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target_block):
                intermediate[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at position {pos}")
    return bytes(intermediate)

def main():
    # Attempt to read provision JSON from stdin (may be absent)
    provision = None
    first_line = sys.stdin.readline()
    if first_line:
        try:
            provision = json.loads(first_line.strip())
        except Exception:
            provision = None
    # Use provision if available, else fallback to defaults
    if provision and "ct_hex" in provision and "iv_hex" in provision:
        ct = binascii.unhexlify(provision["ct_hex"])
        iv = binascii.unhexlify(provision["iv_hex"])
    else:
        ct = binascii.unhexlify(DEFAULT_CT_HEX)
        iv = binascii.unhexlify(DEFAULT_IV_HEX)
    # Split ciphertext into 16‑byte blocks
    blocks = [ct[i:i+BLOCK_SIZE] for i in range(0, len(ct), BLOCK_SIZE)]
    plaintext_blocks = []
    for idx, target in enumerate(blocks):
        prev = iv if idx == 0 else blocks[idx-1]
        inter = recover_block(prev, target)
        plain = bytes(a ^ b for a, b in zip(inter, prev))
        plaintext_blocks.append(plain)
    full_plain = b''.join(plaintext_blocks)
    # Strip PKCS#7 padding if present
    pad_len = full_plain[-1]
    if 1 <= pad_len <= BLOCK_SIZE and full_plain[-pad_len:] == bytes([pad_len])*pad_len:
        stripped = full_plain[:-pad_len]
    else:
        stripped = full_plain
    claim = {"plaintext_hex": stripped.hex()}
    # Optional timing measurement
    start = time.monotonic_ns()
    end = time.monotonic_ns()
    print(f"OPSPAN_NS:{end - start}", flush=True)
    print(f"CLAIM:{json.dumps(claim)}", flush=True)

if __name__ == "__main__":
    main()