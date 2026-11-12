#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev, target):
    """Query the padding oracle with two 16-byte blocks."""
    query = forged_prev + target
    query_b64 = base64.b64encode(query).decode()
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(input())
    return response["pad_ok"]

def decrypt_block(prev_block, target_block):
    """Decrypt a single 16-byte block using padding oracle."""
    intermediate = bytearray(16)
    
    for pad_len in range(1, 17):
        target_pos = 16 - pad_len
        
        forged = bytearray(16)
        
        # Set already-known bytes to produce the current padding length
        for i in range(target_pos + 1, 16):
            forged[i] = intermediate[i] ^ pad_len
        
        # Brute-force the unknown byte
        found = False
        candidates = []
        
        for guess in range(256):
            forged[target_pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                candidates.append(guess)
        
        if not candidates:
            raise Exception(f"Failed to find valid padding at position {target_pos}")
        
        # Handle pad_len == 1 ambiguity: valid padding could be \x01 or \x02\x02, etc.
        if pad_len == 1 and len(candidates) > 1:
            # Test which candidate gives us true \x01 padding by forcing \x02\x02
            for guess in candidates:
                # Set this byte to produce \x02 in plaintext
                test_forged = bytearray(16)
                test_forged[15] = guess ^ 0x01 ^ 0x02  # Change from \x01 to \x02
                test_forged[14] = 0  # This should produce \x02 as well if we found right byte
                
                # Try all values for position 14 to produce \x02
                found_pair = False
                for g14 in range(256):
                    test_forged[14] = g14
                    if padding_oracle(bytes(test_forged), target_block):
                        # This confirms we can make \x02\x02 padding
                        intermediate[15] = guess ^ 0x01
                        found_pair = True
                        break
                
                if found_pair:
                    found = True
                    break
        else:
            # Use the first (or only) candidate
            intermediate[target_pos] = candidates[0] ^ pad_len
            found = True
        
        if not found:
            raise Exception(f"Failed to resolve ambiguity at position {target_pos}")
    
    # XOR intermediate with actual previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    start_time = time.monotonic_ns()
    
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    ct_bytes = bytes.fromhex(task['public_input']['ct_hex'])
    iv = bytes.fromhex(task['public_input']['iv_hex'])
    
    # Split ciphertext into 16-byte blocks
    blocks = [ct_bytes[i:i+16] for i in range(0, len(ct_bytes), 16)]
    
    # Decrypt each block using the padding oracle
    plaintext_blocks = []
    
    # Build chain: IV -> block[0] -> block[1] -> ...
    prev = iv
    for block in blocks:
        decrypted_block = decrypt_block(prev, block)
        plaintext_blocks.append(decrypted_block)
        prev = block
    
    # Concatenate all plaintext blocks
    plaintext_padded = b''.join(plaintext_blocks)
    
    # Remove PKCS#7 padding
    pad_len = plaintext_padded[-1]
    if 1 <= pad_len <= 16:
        # Verify padding is valid
        if all(b == pad_len for b in plaintext_padded[-pad_len:]):
            plaintext = plaintext_padded[:-pad_len]
        else:
            plaintext = plaintext_padded
    else:
        plaintext = plaintext_padded
    
    end_time = time.monotonic_ns()
    
    # Output claim
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext.hex()})}")
    print(f"OPSPAN_NS:{end_time - start_time}")

if __name__ == '__main__':
    main()