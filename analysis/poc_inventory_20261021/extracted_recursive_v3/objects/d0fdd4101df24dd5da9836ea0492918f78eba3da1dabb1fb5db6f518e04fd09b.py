#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev, target_block):
    """Query the padding oracle with two blocks."""
    query_bytes = forged_prev + target_block
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(sys.stdin.readline())
    return response["pad_ok"]

def decrypt_block(target_block, prev_block):
    """Decrypt a single 16-byte block using padding oracle."""
    # We'll recover the intermediate state I, where plaintext = I XOR prev_block
    intermediate = bytearray(16)
    
    # Work backwards from byte 15 to byte 0
    for pad_len in range(1, 17):
        # We're trying to create padding of length pad_len
        # Bytes we've already found need to be set to produce pad_len
        forged = bytearray(16)
        for i in range(16 - pad_len + 1, 16):
            forged[i] = intermediate[i] ^ pad_len
        
        # Now find the byte at position 16 - pad_len
        target_pos = 16 - pad_len
        found = False
        
        for guess in range(256):
            forged[target_pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # Possible valid padding
                # Need to verify this is actual pad_len padding, not a longer padding
                if pad_len == 1:
                    # For pad_len=1, we need to distinguish \x01 from \x02\x02, etc.
                    # Try changing the previous byte; if it still validates, we have longer padding
                    if target_pos > 0:
                        forged_test = forged.copy()
                        forged_test[target_pos - 1] ^= 1
                        if padding_oracle(bytes(forged_test), target_block):
                            # Still valid, so this is part of longer padding, keep searching
                            continue
                
                # Found the right value
                intermediate[target_pos] = guess ^ pad_len
                found = True
                break
        
        if not found:
            raise Exception(f"Failed to find byte at position {target_pos}")
    
    # Recover plaintext by XORing intermediate with actual previous block
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    start_ns = time.monotonic_ns()
    
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    ct_bytes = bytes.fromhex(task['public_input']['ct_hex'])
    iv_bytes = bytes.fromhex(task['public_input']['iv_hex'])
    
    # Split ciphertext into 16-byte blocks
    blocks = [ct_bytes[i:i+16] for i in range(0, len(ct_bytes), 16)]
    
    # Decrypt each block
    plaintext_blocks = []
    
    # First block uses IV as previous
    plaintext_blocks.append(decrypt_block(blocks[0], iv_bytes))
    
    # Remaining blocks use previous ciphertext block
    for i in range(1, len(blocks)):
        plaintext_blocks.append(decrypt_block(blocks[i], blocks[i-1]))
    
    # Concatenate all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    
    end_ns = time.monotonic_ns()
    
    # Output the claim
    print(f"CLAIM:{json.dumps({'plaintext_hex': full_plaintext.hex()})}")
    print(f"OPSPAN_NS:{end_ns - start_ns}")

if __name__ == '__main__':
    main()