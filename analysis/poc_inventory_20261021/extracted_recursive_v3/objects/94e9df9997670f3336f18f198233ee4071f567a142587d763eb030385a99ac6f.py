import sys, json, base64, time

CT_HEX = "6fd6b5558ccd5c58d86f6395552acc8bd904f94179e1131c8c967ab3bb27d9e7949e6a3a1cb04788d17f193efab831c1c098937e523d59ac9b4c500856c3c94775cf55d0f29a7138388ac221d84a8cc5"
IV_HEX = "ff4a7513309279baf8f871b8aa07821d"

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def oracle_query(query_bytes):
    """query_bytes must be exactly 32 bytes (two blocks)."""
    b64 = base64.b64encode(query_bytes).decode()
    print(json.dumps({"q": b64}))
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return False
    resp = json.loads(line.strip())
    return resp.get("pad_ok", False)

def decrypt_block(Ci, prev_C):
    """Return Di = AES_decrypt_key(Ci) using padding oracle."""
    D = [0] * 16
    forged = [0] * 16
    for k in range(1, 17):  # k = number of bytes we have solved from the end
        pos = 16 - k          # index we are solving now
        pad_val = k
        # set forged bytes for already solved positions (pos+1 .. 15)
        for j in range(pos + 1, 16):
            forged[j] = D[j] ^ pad_val
        # brute force the current byte
        found = False
        for guess in range(256):
            forged[pos] = guess
            query = bytes(forged) + Ci
            if oracle_query(query):
                D[pos] = forged[pos] ^ pad_val
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to decrypt byte at pos {pos} for block")
    return bytes(D)

def pkcs7_unpad(padded):
    if not padded:
        return b''
    pad_len = padded[-1]
    if pad_len < 1 or pad_len > 16:
        return padded  # invalid, return as is
    if padded[-pad_len:] != bytes([pad_len]) * pad_len:
        return padded
    return padded[:-pad_len]

def main():
    start = time.monotonic_ns()
    ct = bytes.fromhex(CT_HEX)
    iv = bytes.fromhex(IV_HEX)
    # split into blocks
    blocks = [iv] + [ct[i:i+16] for i in range(0, len(ct), 16)]  # C0..C5
    # we expect len(blocks) = 6 (iv + 5 ciphertext blocks)
    plaintext_blocks = []
    for i in range(1, len(blocks)):
        Ci = blocks[i]
        prev_C = blocks[i-1]
        Di = decrypt_block(Ci, prev_C)
        Pi = xor_bytes(Di, prev_C)
        plaintext_blocks.append(Pi)
    padded_plaintext = b''.join(plaintext_blocks)
    plaintext = pkcs7_unpad(padded_plaintext)
    end = time.monotonic_ns()
    # According to spec, we can give either padded or unpadded; verifier strips padding.
    # We'll give unpadded.
    claim = {"plaintext_hex": plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end - start}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()