#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev, target):
    """Query the padding oracle with forged_prev || target."""
    query_bytes = forged_prev + target
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(input())
    return response["pad_ok"]

def decrypt_block(target_block, prev_block):
    """Decrypt a single 16-byte block using padding oracle."""
    # We'll recover the intermediate state I, where plaintext = I XOR prev_block
    intermediate = bytearray(16)
    
    for pad_len in range(1, 17):
        # We're looking for padding of length pad_len
        # Set up the known suffix to produce valid padding
        forged = bytearray(16)
        for i in range(16 - pad_len + 1, 16):
            forged[i] = intermediate[i] ^ pad_len
        
        # Brute force the byte at position 16 - pad_len
        target_pos = 16 - pad_len
        found = False
        
        for guess in range(256):
            forged[target_pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # Check for false positive when pad_len == 1
                if pad_len == 1:
                    # Verify by changing the second-to-last byte
                    test_forged = bytearray(forged)
                    test_forged[14] ^= 1
                    if not padding_oracle(bytes(test_forged), target_block):
                        # This was a real \x01 padding
                        intermediate[target_pos] = guess ^ pad_len
                        found = True
                        break
                    # Otherwise it was \x02\x02 or longer, continue searching
                else:
                    intermediate[target_pos] = guess ^ pad_len
                    found = True
                    break
        
        if not found:
            raise ValueError(f"Failed to find valid byte at position {target_pos}")
    
    # Recover plaintext from intermediate
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
    
    # Decrypt each block
    plaintext_blocks = []
    prev = iv
    
    for block in blocks:
        pt_block = decrypt_block(block, prev)
        plaintext_blocks.append(pt_block)
        prev = block
    
    # Concatenate all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    
    end_time = time.monotonic_ns()
    
    # Output the claim
    claim = {"plaintext_hex": full_plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end_time - start_time}")

if __name__ == '__main__':
    main()