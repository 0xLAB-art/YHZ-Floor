import sys
import base64
import json
import time

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def query_oracle(forged_prev, target_block):
    query = forged_prev + target_block
    print(json.dumps({"q": base64.b64encode(query).decode()}), flush=True)
    response = sys.stdin.readline()
    if not response:
        return False
    data = json.loads(response.strip())
    return data.get("pad_ok", False)

def decrypt_block(target_block, prev_block):
    """Decrypt a single block using the padding oracle.
    Returns D(target_block) (the raw decrypted block before XOR with prev_block)."""
    decrypted = bytearray(16)  # This will hold D(target_block)
    forged_prev = bytearray(16)
    
    for pos in range(15, -1, -1):
        padding_value = 16 - pos
        
        # Set already discovered bytes to produce correct padding
        for j in range(pos + 1, 16):
            forged_prev[j] = decrypted[j] ^ padding_value
        
        # Try all 256 values for current position
        found = False
        for guess in range(256):
            forged_prev[pos] = guess
            if query_oracle(bytes(forged_prev), target_block):
                decrypted[pos] = forged_prev[pos] ^ padding_value
                found = True
                break
        
        if not found:
            # This shouldn't happen with a proper oracle
            raise RuntimeError(f"Failed to find byte at position {pos}")
    
    return bytes(decrypted)

def main():
    start_time = time.monotonic_ns()
    
    ct_hex = "d4fd1ae8f74b884f431399dd9370e0e634568c178fc39713bcab59917dd7363800fd3b81990efff887b771c7a496f5ec5dbe2ce62015477c0260ca1770dc4ab3d6d9cef769986b8a4a8482c135251af1"
    iv_hex = "1a1816f4b6126fda2c45faa1d395cb47"
    
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into 16-byte blocks
    block_size = 16
    num_blocks = len(ct) // block_size
    ciphertext_blocks = [ct[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    # Decrypt each block from last to first
    plaintext_blocks = []
    prev_block = iv
    
    for i in range(num_blocks - 1, -1, -1):
        target_block = ciphertext_blocks[i]
        decrypted_block = decrypt_block(target_block, prev_block)
        plaintext_block = xor_bytes(decrypted_block, prev_block)
        plaintext_blocks.insert(0, plaintext_block)
        prev_block = target_block
    
    full_plaintext = b''.join(plaintext_blocks)
    
    # Remove PKCS#7 padding
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= 16:
        if all(b == pad_len for b in full_plaintext[-pad_len:]):
            full_plaintext = full_plaintext[:-pad_len]
    
    end_time = time.monotonic_ns()
    
    print(f"OPSPAN_NS:{end_time - start_time}", flush=True)
    print(f"CLAIM:{json.dumps({'plaintext_hex': full_plaintext.hex()})}", flush=True)

if __name__ == "__main__":
    main()