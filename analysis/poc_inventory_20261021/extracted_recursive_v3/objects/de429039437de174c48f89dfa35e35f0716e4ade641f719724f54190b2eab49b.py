import sys, base64, time

# Hard‑coded provisioned values
ct_hex = "597ffc05ced12ea900dc1c68a308271272049f17fe8503e93cae0dfb069473d1185e1d67aa85c7d84678c299e008039eab8191074f28c129c590568508ba834056916a4fbeddc41c923577a28cecc381"
iv_hex = "bb15c9e0f618383a43257ed3bf54754d"
block_size = 16

ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)
blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]

def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    payload = forged_prev + target  # 32 bytes
    b64 = base64.b64encode(payload).decode()
    # Emit JSON without extra spaces as required by protocol
    sys.stdout.write('{"q":"' + b64 + '"}\n')
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)
    # Expected format: {"pad_ok":true} or {"pad_ok":false}
    # Simple parsing without json module to avoid whitespace issues
    line = line.strip()
    if 'true' in line:
        return True
    return False

plaintext_blocks = []
start_ns = time.monotonic_ns()

for idx, target in enumerate(blocks):
    prev = iv if idx == 0 else blocks[idx-1]
    intermediate = bytearray(block_size)
    # Recover bytes from last to first
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        forged = bytearray(block_size)
        # Set suffix bytes to enforce correct padding
        for j in range(pos+1, block_size):
            forged[j] = intermediate[j] ^ pad_val
        found = False
        for guess in range(256):
            forged[pos] = guess
            if oracle_query(bytes(forged), target):
                # Verify that this guess is not a false positive when pad_val == 1
                # For pad_val == 1, try a second check by modifying another byte
                if pad_val == 1:
                    # Flip a different byte and ensure padding still fails
                    forged[pos] ^= 0x01
                    if oracle_query(bytes(forged), target):
                        # Still true, likely false positive; revert and continue
                        forged[pos] ^= 0x01
                        continue
                    forged[pos] ^= 0x01  # revert to original guess
                intermediate[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            sys.stderr.write(f"Failed to recover byte idx={idx} pos={pos}\n")
            sys.exit(1)
    # Plaintext block = intermediate XOR previous ciphertext (or IV)
    plain_block = bytes(a ^ b for a, b in zip(intermediate, prev))
    plaintext_blocks.append(plain_block)

plaintext = b''.join(plaintext_blocks)
end_ns = time.monotonic_ns()

claim = {"plaintext_hex": plaintext.hex()}
sys.stdout.write('CLAIM:' + str(claim).replace("'", '"') + '\n')
sys.stdout.write('OPSPAN_NS:' + str(end_ns - start_ns) + '\n')
sys.stdout.flush()