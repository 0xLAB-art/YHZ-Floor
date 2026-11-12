import sys
import base64
import json
import time

def query_oracle(forged_prev: bytes, target: bytes) -> bool:
    """Send a padding oracle query and return the result."""
    q = forged_prev + target
    assert len(q) == 32
    print(json.dumps({"q": base64.b64encode(q).decode()}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise EOFError("Oracle closed connection")
    resp = json.loads(line.strip())
    return resp["pad_ok"]

def decrypt_block(prev_block: bytes, target_block: bytes) -> bytes:
    """Decrypt a single CBC block using the padding oracle.
    Returns the intermediate state D(target_block)."""
    intermediate = bytearray(16)
    forged = bytearray(prev_block)  # start with original prev block
    
    for pos in reversed(range(16)):  # 15 down to 0
        pad_val = 16 - pos
        
        # Set bytes after pos to maintain correct padding
        for k in range(pos + 1, 16):
            forged[k] = intermediate[k] ^ pad_val
        
        # Try all 256 values for this position
        found = False
        for guess in range(256):
            forged[pos] = guess
            if query_oracle(bytes(forged), target_block):
                intermediate[pos] = guess ^ pad_val
                found = True
                break
        
        if not found:
            raise ValueError(f"Failed to find byte at position {pos}")
    
    return bytes(intermediate)

def main():
    ct_hex = "2bdb1d926ed87249f36645b93e80d9ae37e6729f594d10db67fb184f8c335f3334bd893e2abf709f046c893f85d3b31e17087e0a79110ccec5354f2f3b1553bda724f35cfec372c7021db228ba146572"
    iv_hex = "95b968fc0567c1d73141b1902f61e7b7"
    
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split into 16-byte blocks
    block_size = 16
    num_blocks = len(ct) // block_size
    assert num_blocks == 5
    
    c_blocks = [ct[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    start_ns = time.monotonic_ns()
    
    # Decrypt each block
    plaintext_blocks = []
    prev = iv
    for i in range(num_blocks):
        intermediate = decrypt_block(prev, c_blocks[i])
        # Plaintext = intermediate XOR previous ciphertext block (or IV)
        p_block = bytes(a ^ b for a, b in zip(intermediate, prev))
        plaintext_blocks.append(p_block)
        prev = c_blocks[i]
    
    # Combine all plaintext blocks (80 bytes with padding)
    full_plaintext = b''.join(plaintext_blocks)
    
    # Strip PKCS#7 padding
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= 16:
        if all(b == pad_len for b in full_plaintext[-pad_len:]):
            unpadded = full_plaintext[:-pad_len]
        else:
            unpadded = full_plaintext
    else:
        unpadded = full_plaintext
    
    end_ns = time.monotonic_ns()
    
    # Claim: return the 64-byte unpadded message
    print(f"CLAIM:{json.dumps({'plaintext_hex': unpadded.hex()})}")
    print(f"OPSPAN_NS:{end_ns - start_ns}", flush=True)

if __name__ == "__main__":
    main()