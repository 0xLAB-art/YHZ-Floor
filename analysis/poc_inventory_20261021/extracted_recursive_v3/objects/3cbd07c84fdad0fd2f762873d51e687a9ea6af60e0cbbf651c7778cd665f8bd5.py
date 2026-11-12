#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev, target):
    """Query the padding oracle with two blocks."""
    query = forged_prev + target
    query_b64 = base64.b64encode(query).decode()
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(sys.stdin.readline())
    return response["pad_ok"]

def decrypt_block(target_block, prev_block):
    """Decrypt a single 16-byte block using padding oracle."""
    intermediate = bytearray(16)
    
    for pad_len in range(1, 17):
        forged = bytearray(16)
        
        # Set already-known bytes to produce the target padding value
        for i in range(pad_len - 1):
            forged[15 - i] = intermediate[15 - i] ^ pad_len
        
        # Brute force the current byte position
        byte_pos = 16 - pad_len
        candidates = []
        
        for guess in range(256):
            forged[byte_pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                candidates.append(guess)
        
        if len(candidates) == 0:
            raise Exception(f"No valid padding found for byte at position {byte_pos}")
        
        # Handle the case where we find multiple candidates
        if pad_len == 1 and len(candidates) > 1:
            # Multiple valid values means we might be hitting existing padding
            # We need to distinguish between 0x01 and 0x02 0x02, etc.
            for guess in candidates:
                # Test if this is really 0x01 by changing another byte
                verify_forged = bytearray(16)
                verify_forged[15] = guess
                verify_forged[14] = 0xFF  # Arbitrary different value
                
                if not padding_oracle(bytes(verify_forged), target_block):
                    # Padding broke when we changed byte 14, so this is true 0x01
                    intermediate[15] = guess ^ 0x01
                    break
            else:
                # If none worked with the test, just take the first candidate
                intermediate[15] = candidates[0] ^ 0x01
        else:
            # For pad_len > 1 or single candidate, use the first/only candidate
            intermediate[byte_pos] = candidates[0] ^ pad_len
    
    # XOR intermediate with actual previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    start_time = time.monotonic_ns()
    
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    ct_hex = instance['public_input']['ct_hex']
    iv_hex = instance['public_input']['iv_hex']
    
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into 16-byte blocks
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    
    # Decrypt each block
    plaintext_blocks = []
    prev = iv
    
    for block in blocks:
        pt_block = decrypt_block(block, prev)
        plaintext_blocks.append(pt_block)
        prev = block
    
    # Combine plaintext
    plaintext = b''.join(plaintext_blocks)
    
    # Strip PKCS#7 padding
    if len(plaintext) > 0:
        pad_len = plaintext[-1]
        if isinstance(pad_len, int) and 1 <= pad_len <= 16:
            if all(b == pad_len for b in plaintext[-pad_len:]):
                plaintext = plaintext[:-pad_len]
    
    end_time = time.monotonic_ns()
    
    plaintext_hex = plaintext.hex()
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}")
    print(f"OPSPAN_NS:{end_time - start_time}")

if __name__ == '__main__':
    main()