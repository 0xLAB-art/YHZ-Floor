import sys, json, base64, time

def read_provision():
    # The verifier sends a single JSON line with the provisioned material.
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)
    prov = json.loads(line)
    ct = bytes.fromhex(prov["ct_hex"])
    iv = bytes.fromhex(prov["iv_hex"])
    # split ciphertext into 16‑byte blocks
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    return iv, blocks

def query(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    resp_line = sys.stdin.readline()
    if not resp_line:
        sys.exit(1)
    resp = json.loads(resp_line)
    return bool(resp.get("pad_ok"))

def recover_intermediate(target_block: bytes) -> bytes:
    block_size = 16
    intermediate = bytearray(block_size)
    forged = bytearray(block_size)
    # iterate from last byte to first
    for pos in range(block_size - 1, -1, -1):
        pad_val = block_size - pos
        # set already‑known positions to enforce padding
        for i in range(pos + 1, block_size):
            forged[i] = intermediate[i] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query(bytes(forged), target_block):
                intermediate[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at position {pos}")
    return bytes(intermediate)

def pkcs7_unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding")
    return data[:-pad_len]

def main():
    start_ns = time.monotonic_ns()
    iv, blocks = read_provision()
    plaintext_blocks = []
    prev = iv
    for block in blocks:
        intermediate = recover_intermediate(block)
        pt_block = bytes(a ^ b for a, b in zip(intermediate, prev))
        plaintext_blocks.append(pt_block)
        prev = block
    padded_plain = b"".join(plaintext_blocks)
    try:
        plaintext = pkcs7_unpad(padded_plain)
    except Exception:
        plaintext = padded_plain
    duration = time.monotonic_ns() - start_ns
    sys.stdout.write(f"OPSPAN_NS:{duration}\n")
    sys.stdout.flush()
    claim = {"plaintext_hex": plaintext.hex()}
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()