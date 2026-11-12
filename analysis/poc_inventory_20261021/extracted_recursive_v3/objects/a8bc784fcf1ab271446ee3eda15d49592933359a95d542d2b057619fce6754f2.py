#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev, target_block):
    """Query the padding oracle with forged_prev || target_block."""
    query = forged_prev + target_block
    query_b64 = base64.b64encode(query).decode('ascii')
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(sys.stdin.readline())
    return response["pad_ok"]

def decrypt_block(prev_block, target_block):
    """Recover plaintext of target_block using padding oracle."""
    intermediate = bytearray(16)
    
    for pad_len in range(1, 17):
        pos = 16 - pad_len
        
        # Build forged block: already-known positions set to produce pad_len
        forged = bytearray(16)
        for i in range(pos + 1, 16):
            forged[i] = intermediate[i] ^ pad_len
        
        # Brute force the byte at position pos
        found = False
        candidates = []
        
        for guess in range(256):
            forged[pos] = guess
            if padding_oracle(bytes(forged), target_block):
                candidates.append(guess)
        
        if not candidates:
            raise Exception(f"No valid padding found at position {pos}")
        
        # For pad_len == 1, we might get multiple candidates due to natural padding
        if pad_len == 1 and len(candidates) > 1:
            # Try flipping the previous byte to disambiguate
            for guess in candidates:
                test_forged = bytearray(16)
                for i in range(pos + 1, 16):
                    test_forged[i] = intermediate[i] ^ pad_len
                test_forged[pos] = guess
                test_forged[pos - 1] = test_forged[pos - 1] ^ 1
                
                if not padding_oracle(bytes(test_forged), target_block):
                    # This one is the true 0x01 padding
                    intermediate[pos] = guess ^ pad_len
                    found = True
                    break
            
            if not found:
                # If all still valid, pick the first (shouldn't happen normally)
                intermediate[pos] = candidates[0] ^ pad_len
        else:
            intermediate[pos] = candidates[0] ^ pad_len
    
    # XOR intermediate with actual previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    start_time = time.monotonic_ns()
    
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    ct_bytes = bytes.fromhex(task["public_input"]["ct_hex"])
    iv = bytes.fromhex(task["public_input"]["iv_hex"])
    
    # Split ciphertext into blocks
    blocks = [ct_bytes[i:i+16] for i in range(0, len(ct_bytes), 16)]
    
    # Decrypt each block
    plaintext_blocks = []
    prev = iv
    
    for block in blocks:
        pt_block = decrypt_block(prev, block)
        plaintext_blocks.append(pt_block)
        prev = block
    
    plaintext = b''.join(plaintext_blocks)
    
    # Strip PKCS#7 padding
    pad_len = plaintext[-1]
    if 1 <= pad_len <= 16:
        if all(b == pad_len for b in plaintext[-pad_len:]):
            plaintext = plaintext[:-pad_len]
    
    end_time = time.monotonic_ns()
    
    print(f"OPSPAN_NS:{end_time - start_time}")
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext.hex()})}")

if __name__ == "__main__":
    main()