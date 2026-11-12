import sys
import base64
import json
import time

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def query_oracle(forged_prev, target_block):
    """Send padding oracle query and return pad_ok boolean."""
    query = forged_prev + target_block
    q_b64 = base64.b64encode(query).decode()
    print(json.dumps({"q": q_b64}), flush=True)
    line = sys.stdin.readline()
    if not line:
        return False
    resp = json.loads(line.strip())
    return resp.get("pad_ok", False)

def decrypt_block(prev_block, target_block):
    """Decrypt a single 16-byte block using padding oracle."""
    decrypted = bytearray(16)  # This will hold Decrypt(target_block)
    forged_prev = bytearray(16)
    
    for pos in range(15, -1, -1):
        pad_val = 16 - pos
        
        # Set already-decrypted positions to produce correct padding
        for i in range(pos + 1, 16):
            forged_prev[i] = decrypted[i] ^ pad_val
        
        # Try all 256 values for current position
        found = False
        for guess in range(256):
            forged_prev[pos] = guess
            if query_oracle(bytes(forged_prev), target_block):
                # Found! decrypted[pos] ^ guess = pad_val
                decrypted[pos] = guess ^ pad_val
                found = True
                break
        
        if not found:
            # This shouldn't happen with a proper oracle
            raise RuntimeError(f"Failed to decrypt byte at position {pos}")
    
    # Now compute plaintext: P = Decrypt(C) XOR prev_block
    plaintext = xor_bytes(decrypted, prev_block)
    return plaintext

def main():
    start_ns = time.monotonic_ns()
    
    ct_hex = "13d6445e67c95661ec4f0160f34273037263acd273555f1becd5ca803377d25fc62480d69e12b07200e08bd155222159158910b81376ab00358bed9888eb0c241ce9b2ad8e29af845388228db2136e7a"
    iv_hex = "e6a13d9d5e3939442b29e73ca4e867da"
    
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    
    # Split ciphertext into blocks
    num_blocks = len(ct) // block_size
    ciphertext_blocks = [ct[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    # Decrypt each block
    plaintext_blocks = []
    prev = iv
    for i, block in enumerate(ciphertext_blocks):
        pt_block = decrypt_block(prev, block)
        plaintext_blocks.append(pt_block)
        prev = block  # Next block uses this ciphertext as "previous"
    
    full_plaintext = b''.join(plaintext_blocks)
    
    # Remove PKCS#7 padding
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= 16:
        if all(b == pad_len for b in full_plaintext[-pad_len:]):
            full_plaintext = full_plaintext[:-pad_len]
    
    end_ns = time.monotonic_ns()
    
    print(f"CLAIM:{{\"plaintext_hex\": \"{full_plaintext.hex()}\"}}", flush=True)
    print(f"OPSPAN_NS:{end_ns - start_ns}", flush=True)

if __name__ == "__main__":
    main()