#!/usr/bin/env python3
"""
CBC padding oracle attack solver.
Recovers plaintext by exploiting PKCS#7 padding validation.
"""

import sys
import json
import base64
import time

def padding_oracle(forged_prev_block, target_block):
    """Query the padding oracle with two blocks."""
    query_bytes = forged_prev_block + target_block
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    
    query_obj = {"q": query_b64}
    print(json.dumps(query_obj), flush=True)
    
    response_line = sys.stdin.readline().strip()
    response_obj = json.loads(response_line)
    return response_obj["pad_ok"]

def recover_block(target_block, prev_block):
    """Recover one plaintext block using padding oracle."""
    block_size = 16
    intermediate = bytearray(block_size)
    
    # For each padding length from 1 to block_size
    for pad_len in range(1, block_size + 1):
        # Construct the forged previous block
        forged = bytearray(block_size)
        
        # Set known bytes to produce the target padding
        for i in range(1, pad_len):
            pos = block_size - i
            forged[pos] = intermediate[pos] ^ pad_len
        
        # Brute force the current byte
        pos = block_size - pad_len
        found = False
        
        for guess in range(256):
            forged[pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # Valid padding found
                intermediate[pos] = guess ^ pad_len
                found = True
                break
        
        if not found:
            raise Exception(f"Failed to find valid byte at position {pos}")
    
    # XOR intermediate with actual previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(block_size))
    return plaintext

def main():
    start_ns = time.monotonic_ns()
    
    # Read task instance
    instance_path = sys.argv[1]
    with open(instance_path, 'r') as f:
        instance = json.load(f)
    
    public_input = instance["public_input"]
    ct_hex = public_input["ct_hex"]
    iv_hex = public_input["iv_hex"]
    
    # Parse ciphertext and IV
    ct_bytes = bytes.fromhex(ct_hex)
    iv_bytes = bytes.fromhex(iv_hex)
    
    block_size = 16
    num_blocks = len(ct_bytes) // block_size
    
    # Split ciphertext into blocks
    ct_blocks = [ct_bytes[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    # Recover each block
    plaintext_blocks = []
    prev_block = iv_bytes
    
    for i, ct_block in enumerate(ct_blocks):
        pt_block = recover_block(ct_block, prev_block)
        plaintext_blocks.append(pt_block)
        prev_block = ct_block
    
    # Combine plaintext
    full_plaintext = b''.join(plaintext_blocks)
    
    end_ns = time.monotonic_ns()
    opspan_ns = end_ns - start_ns
    
    # Output claim
    plaintext_hex = full_plaintext.hex()
    claim = {"plaintext_hex": plaintext_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{opspan_ns}")

if __name__ == "__main__":
    main()