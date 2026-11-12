import sys, json, base64, time

CT_HEX = "6fd6b5558ccd5c58d86f6395552acc8bd904f94179e1131c8c967ab3bb27d9e7949e6a3a1cb04788d17f193efab831c1c098937e523d59ac9b4c500856c3c94775cf55d0f29a7138388ac221d84a8cc5"
IV_HEX = "ff4a7513309279baf8f871b8aa07821d"

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def oracle_query(query_bytes):
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
    for k in range(1, 17):
        pos = 16 - k
        pad_val = k
        # set forged bytes for already solved positions
        for j in range(pos + 1, 16):
            forged[j] = D[j] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess
            query = bytes(forged) + Ci
            if oracle_query(query):
                # Optional: verify with a second test to avoid false positives
                # We'll do a simple verification: change the second last byte (if exists) and see if padding breaks
                # For k==1, we can't verify easily; we'll assume it's correct.
                # For k>1, we can do a verification by flipping a bit in a known byte and expecting failure.
                if k == 1:
                    D[pos] = guess ^ pad_val
                    found = True
                    break
                else:
                    # verification: temporarily change forged[pos+1] by 1 and query; should fail if correct
                    orig = forged[pos+1]
                    forged[pos+1] = (forged[pos+1] + 1) & 0xFF
                    query2 = bytes(forged) + Ci
                    if not oracle_query(query2):
                        forged[pos+1] = orig  # restore
                        D[pos] = guess ^ pad_val
                        found = True
                        break
                    forged[pos+1] = orig  # restore
        if not found:
            raise RuntimeError(f"Failed to decrypt byte at pos {pos} for block")
    return bytes(D)

def pkcs7_unpad(padded):
    if not padded:
        return b''
    pad_len = padded[-1]
    if pad_len < 1 or pad_len > 16:
        return padded
    if padded[-pad_len:] != bytes([pad_len]) * pad_len:
        return padded
    return padded[:-pad_len]

def main():
    start = time.monotonic_ns()
    ct = bytes.fromhex(CT_HEX)
    iv = bytes.fromhex(IV_HEX)
    blocks = [iv] + [ct[i:i+16] for i in range(0, len(ct), 16)]
    plaintext_blocks = []
    for i in range(1, len(blocks)):
        Ci = blocks[i]
        prev_C = blocks[i-1]
        sys.stderr.write(f"Decrypting block {i}\n")
        sys.stderr.flush()
        Di = decrypt_block(Ci, prev_C)
        Pi = xor_bytes(Di, prev_C)
        plaintext_blocks.append(Pi)
        sys.stderr.write(f"  P{i} = {Pi.hex()}\n")
        sys.stderr.flush()
    padded_plaintext = b''.join(plaintext_blocks)
    plaintext = pkcs7_unpad(padded_plaintext)
    end = time.monotonic_ns()
    claim = {"plaintext_hex": plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end - start}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
"
}
}]}