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
        # We're looking for padding of length pad_len
        # Build the prefix that will cause valid padding
        forged = bytearray(16)
        
        # Set known bytes to produce the target padding
        for i in range(1, pad_len):
            forged[16 - i] = intermediate[16 - i] ^ pad_len
        
        # Brute force the current byte
        found = False
        for guess in range(256):
            forged[16 - pad_len] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # Valid padding found
                # When we get valid padding, intermediate[16-pad_len] ^ guess = pad_len
                intermediate[16 - pad_len] = guess ^ pad_len
                
                # Special case: when pad_len=1, verify it's actually 0x01 padding
                if pad_len == 1:
                    # Change second-to-last byte and verify padding breaks
                    test_forged = bytearray(forged)
                    test_forged[14] ^= 1
                    if padding_oracle(bytes(test_forged), target_block):
                        # Still valid - we have longer padding, not 0x01
                        continue
                
                found = True
                break
        
        if not found:
            # If pad_len=1 failed for all values, the block might already end in valid padding
            # Try another approach: assume the last byte is part of longer padding
            if pad_len == 1:
                for actual_pad in range(2, 17):
                    # Assume padding is 0x02 0x02, 0x03 0x03 0x03, etc.
                    test_forged = bytearray(16)
                    for i in range(actual_pad):
                        test_forged[16 - 1 - i] = actual_pad ^ 0x01
                    if not padding_oracle(bytes(test_forged), target_block):
                        # This breaks it, so original was valid with this padding
                        intermediate[15] = actual_pad ^ 0
                        found = True
                        break
        
        if not found:
            raise Exception(f"Failed to find valid padding for position {16 - pad_len}")
    
    # XOR intermediate with the actual previous block to get plaintext
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
    pad_len = plaintext[-1]
    if 1 <= pad_len <= 16:
        # Verify padding
        if all(b == pad_len for b in plaintext[-pad_len:]):
            plaintext = plaintext[:-pad_len]
    
    end_time = time.monotonic_ns()
    
    plaintext_hex = plaintext.hex()
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}")
    print(f"OPSPAN_NS:{end_time - start_time}")

if __name__ == '__main__':
    main()