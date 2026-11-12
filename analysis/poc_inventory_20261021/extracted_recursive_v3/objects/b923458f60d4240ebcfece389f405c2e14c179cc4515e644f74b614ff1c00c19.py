import sys, json, base64, time

BLOCK_SIZE = 16
# Default provision (will be overwritten if verifier sends a JSON line first)
CT_HEX = "c2fdd5bba0f0f34b3b12f7d55df98c02658eb764338d0c2cbaf7580a645468dc34b8e459e70ca5209b7a6bf4fcd23a2364e9f9f524635518b19ef94990ffae77bfb481c845c32d2ad155cdad959cce28"
IV_HEX = "fd2a7e8ad91248a35cef91621d184830"

def load_provision():
    # The verifier may send a JSON line with the provisioned material.
    # If not, we fall back to the hard‑coded values above.
    line = sys.stdin.readline()
    if not line:
        return bytes.fromhex(IV_HEX), [bytes.fromhex(CT_HEX)[i:i+BLOCK_SIZE] for i in range(0, len(CT_HEX)//2, BLOCK_SIZE)]
    try:
        prov = json.loads(line)
        if isinstance(prov, dict) and "ct_hex" in prov and "iv_hex" in prov:
            ct = bytes.fromhex(prov["ct_hex"])
            iv = bytes.fromhex(prov["iv_hex"])
            blocks = [ct[i:i+BLOCK_SIZE] for i in range(0, len(ct), BLOCK_SIZE)]
            return iv, blocks
    except Exception:
        pass
    # If parsing failed, treat the line as unrelated and use defaults.
    # Put the line back into a buffer for later reads (unlikely needed).
    return bytes.fromhex(IV_HEX), [bytes.fromhex(CT_HEX)[i:i+BLOCK_SIZE] for i in range(0, len(CT_HEX)//2, BLOCK_SIZE)]

def query(forged_prev: bytes, target: bytes) -> bool:
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    resp_line = sys.stdin.readline()
    if not resp_line:
        # No response – treat as padding invalid
        return False
    try:
        resp = json.loads(resp_line)
        return bool(resp.get("pad_ok"))
    except Exception:
        return False

def recover_intermediate(target_block: bytes) -> bytes:
    intermediate = bytearray(BLOCK_SIZE)
    forged = bytearray(BLOCK_SIZE)
    for pos in range(BLOCK_SIZE - 1, -1, -1):
        pad_val = BLOCK_SIZE - pos
        # set already‑known bytes to enforce padding
        for i in range(pos + 1, BLOCK_SIZE):
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
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding")
    return data[:-pad_len]

def main():
    start_ns = time.monotonic_ns()
    iv, blocks = load_provision()
    plaintext_blocks = []
    prev = iv
    for block in blocks:
        interm = recover_intermediate(block)
        pt_block = bytes(a ^ b for a, b in zip(interm, prev))
        plaintext_blocks.append(pt_block)
        prev = block
    padded_plain = b"".join(plaintext_blocks)
    try:
        plain = pkcs7_unpad(padded_plain)
    except Exception:
        plain = padded_plain
    duration = time.monotonic_ns() - start_ns
    # optional timing output
    sys.stdout.write(f"OPSPAN_NS:{duration}\n")
    sys.stdout.flush()
    claim = {"plaintext_hex": plain.hex()}
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()