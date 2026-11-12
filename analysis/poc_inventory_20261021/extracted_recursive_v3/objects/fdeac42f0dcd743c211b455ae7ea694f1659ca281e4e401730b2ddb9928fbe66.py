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
    decrypted = bytearray(16)
    
    for pad_len in range(1, 17):
        # We're discovering byte at position 16 - pad_len (0-indexed: 15, 14, ...)
        target_pos = 16 - pad_len
        
        # Build the forged previous block
        forged = bytearray(16)
        
        # Set already-known bytes to produce the current padding length
        for i in range(target_pos + 1, 16):
            forged[i] = decrypted[i] ^ pad_len
        
        # Brute-force the unknown byte
        found = False
        for guess in range(256):
            forged[target_pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # Valid padding found
                # The decrypted byte XOR guess = pad_len
                decrypted[target_pos] = guess ^ pad_len
                
                # Special case: when pad_len == 1, we need to verify this is truly \x01
                # and not a longer valid padding that happens to end in the right byte
                if pad_len == 1 and guess != 0:
                    # Verify by flipping another byte - if padding is still valid,
                    # we found a longer padding by accident
                    test_forged = bytearray(forged)
                    test_forged[target_pos - 1] ^= 1
                    if padding_oracle(bytes(test_forged), target_block):
                        # Still valid, so this wasn't the right byte for \x01 padding
                        continue
                
                found = True
                break
        
        if not found:
            raise Exception(f"Failed to find valid padding at position {target_pos}")
    
    return bytes(decrypted)

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