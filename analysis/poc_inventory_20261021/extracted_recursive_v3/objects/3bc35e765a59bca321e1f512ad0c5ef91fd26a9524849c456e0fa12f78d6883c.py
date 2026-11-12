#!/usr/bin/env python3
import sys
import json
import base64
from typing import List

def padding_oracle(forged_prev: bytes, target_block: bytes) -> bool:
    """Query the padding oracle with a two-block construction."""
    query = forged_prev + target_block
    query_b64 = base64.b64encode(query).decode('ascii')
    
    # Send query
    query_obj = {"q": query_b64}
    print(json.dumps(query_obj), flush=True)
    
    # Read response
    response_line = sys.stdin.readline().strip()
    response = json.loads(response_line)
    return response["pad_ok"]

def decrypt_block(oracle, prev_block: bytes, ct_block: bytes) -> bytes:
    """
    Decrypt a single ciphertext block using padding oracle attack.
    prev_block: the previous ciphertext block (or IV)
    ct_block: the ciphertext block to decrypt
    Returns: the decrypted plaintext block
    """
    # Intermediate value (what we get after block cipher decryption, before XOR)
    intermediate = bytearray(16)
    
    # Recover byte by byte, starting from the last byte
    for pad_value in range(1, 17):
        # Position we're attacking (0-indexed from the left)
        pos = 16 - pad_value
        
        # Construct forged block that will produce desired padding
        forged = bytearray(16)
        
        # Set already-known bytes to produce the current padding value
        for i in range(pos + 1, 16):
            forged[i] = intermediate[i] ^ pad_value
        
        # Try all possible values for the current byte
        found = False
        for guess in range(256):
            forged[pos] = guess
            
            if oracle(bytes(forged), ct_block):
                # Valid padding found
                # Special case: for pad_value=1, we need to verify it's actually \x01
                # and not \x02\x02, \x03\x03\x03, etc.
                if pad_value == 1:
                    # Change the previous byte and check if padding is still valid
                    # If it's still valid, we likely have longer padding
                    test_forged = bytearray(forged)
                    test_forged[pos - 1] ^= 1  # Flip a bit in previous byte
                    if oracle(bytes(test_forged), ct_block):
                        # Still valid, meaning we hit existing padding, not our crafted \x01
                        continue
                
                # We found the correct value
                intermediate[pos] = guess ^ pad_value
                found = True
                break
        
        if not found:
            raise ValueError(f"Failed to find byte at position {pos}")
    
    # XOR intermediate with previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    # Read task instance
    instance_path = sys.argv[1]
    with open(instance_path, 'r') as f:
        instance = json.load(f)
    
    public_input = instance["public_input"]
    ct_hex = public_input["ct_hex"]
    iv_hex = public_input["iv_hex"]
    
    # Parse ciphertext and IV
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into 16-byte blocks
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    num_blocks = len(blocks)
    
    # Decrypt each block
    plaintext_blocks = []
    
    # First block uses IV as previous
    prev = iv
    for i, block in enumerate(blocks):
        pt_block = decrypt_block(padding_oracle, prev, block)
        plaintext_blocks.append(pt_block)
        prev = block
    
    # Concatenate all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    
    # Output the claim
    claim = {
        "plaintext_hex": full_plaintext.hex()
    }
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()