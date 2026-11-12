#!/usr/bin/env python3
"""
AES-128-CBC Padding Oracle Attack (Vaudenay)
Recovers plaintext by exploiting padding validation oracle.
"""

import sys
import json
import base64
import time

def padding_oracle_query(forged_prev_block, target_block):
    """Query the padding oracle with forged_prev || target."""
    query_bytes = forged_prev_block + target_block
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    query_json = json.dumps({"q": query_b64})
    print(query_json, flush=True)
    
    response_line = sys.stdin.readline().strip()
    response = json.loads(response_line)
    return response["pad_ok"]

def decrypt_block(target_block, prev_block_or_iv):
    """
    Decrypt a single 16-byte block using padding oracle.
    Returns the decrypted intermediate state (before XOR with prev).
    """
    block_size = 16
    intermediate = bytearray(block_size)
    
    # Attack each byte position from right to left
    for pos in range(block_size - 1, -1, -1):
        # Current padding value we're forcing
        padding_value = block_size - pos
        
        # Prepare the forged block
        forged = bytearray(block_size)
        
        # Set known bytes to produce correct padding
        for known_pos in range(pos + 1, block_size):
            forged[known_pos] = intermediate[known_pos] ^ padding_value
        
        # Brute force the current byte
        found = False
        for guess in range(256):
            forged[pos] = guess
            
            if padding_oracle_query(bytes(forged), target_block):
                # Padding is valid
                # The decrypted byte XOR guess = padding_value
                intermediate[pos] = guess ^ padding_value
                
                # Special case: when pos == 15, we might have found valid padding
                # by accident (e.g., original ends in 0x02 0x02)
                if pos == block_size - 1:
                    # Verify by changing the second-to-last byte
                    forged[block_size - 2] ^= 1
                    if not padding_oracle_query(bytes(forged), target_block):
                        # This was a false positive, keep searching
                        continue
                
                found = True
                break
        
        if not found:
            raise RuntimeError(f"Failed to find valid byte at position {pos}")
    
    return bytes(intermediate)

def decrypt_ciphertext(iv, ciphertext_blocks):
    """Decrypt all blocks using the padding oracle."""
    plaintext_blocks = []
    
    # Start with IV as the "previous block"
    prev = iv
    
    for block in ciphertext_blocks:
        # Decrypt to get intermediate state
        intermediate = decrypt_block(block, prev)
        
        # XOR with previous block/IV to get plaintext
        plaintext = bytes(a ^ b for a, b in zip(intermediate, prev))
        plaintext_blocks.append(plaintext)
        
        # Move to next block
        prev = block
    
    return b''.join(plaintext_blocks)

def main():
    start_time = time.monotonic_ns()
    
    # Read task instance
    instance_path = sys.argv[1]
    with open(instance_path, 'r') as f:
        instance = json.load(f)
    
    public_input = instance['public_input']
    ct_hex = public_input['ct_hex']
    iv_hex = public_input['iv_hex']
    
    # Parse ciphertext and IV
    ciphertext = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into 16-byte blocks
    block_size = 16
    ct_blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    
    # Decrypt all blocks
    plaintext_padded = decrypt_ciphertext(iv, ct_blocks)
    
    end_time = time.monotonic_ns()
    opspan = end_time - start_time
    
    # Output the claim (verifier will strip padding if present)
    claim = {"plaintext_hex": plaintext_padded.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{opspan}")

if __name__ == "__main__":
    main()