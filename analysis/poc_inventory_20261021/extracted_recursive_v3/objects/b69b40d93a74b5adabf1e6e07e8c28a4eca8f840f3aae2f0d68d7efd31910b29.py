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
    intermediate = bytearray(16)
    
    for pad_len in range(1, 17):
        forged = bytearray(16)
        
        # Set known bytes to produce padding of pad_len
        for i in range(16 - pad_len + 1, 16):
            forged[i] = intermediate[i] ^ pad_len
        
        target_pos = 16 - pad_len
        candidates = []
        
        # Find all bytes that produce valid padding
        for guess in range(256):
            forged[target_pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                candidates.append(guess)
        
        if not candidates:
            raise ValueError(f"Failed to find valid byte at position {target_pos}")
        
        # For pad_len == 1, we need to disambiguate
        if pad_len == 1 and len(candidates) > 1:
            # Check which candidate is the real \x01 by flipping second-to-last byte
            for guess in candidates:
                forged[target_pos] = guess
                test_forged = bytearray(forged)
                test_forged[14] ^= 1
                if not padding_oracle(bytes(test_forged), target_block):
                    # This one breaks when we modify the previous byte, so it's \x01
                    intermediate[target_pos] = guess ^ pad_len
                    break
            else:
                # If all candidates still work, take the first one
                intermediate[target_pos] = candidates[0] ^ pad_len
        else:
            # Take the first valid candidate
            intermediate[target_pos] = candidates[0] ^ pad_len
    
    # Recover plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    start_time = time.monotonic_ns()
    
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    ct_bytes = bytes.fromhex(task['public_input']['ct_hex'])
    iv = bytes.fromhex(task['public_input']['iv_hex'])
    
    blocks = [ct_bytes[i:i+16] for i in range(0, len(ct_bytes), 16)]
    
    plaintext_blocks = []
    prev = iv
    
    for block in blocks:
        pt_block = decrypt_block(block, prev)
        plaintext_blocks.append(pt_block)
        prev = block
    
    full_plaintext = b''.join(plaintext_blocks)
    
    end_time = time.monotonic_ns()
    
    claim = {"plaintext_hex": full_plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end_time - start_time}")

if __name__ == '__main__':
    main()