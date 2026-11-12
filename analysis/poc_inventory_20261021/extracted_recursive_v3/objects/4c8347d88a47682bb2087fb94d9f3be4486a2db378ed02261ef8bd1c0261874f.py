#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev, target_block):
    """Query the padding oracle with forged_prev || target_block."""
    query_bytes = forged_prev + target_block
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    
    query_obj = {"q": query_b64}
    print(json.dumps(query_obj), flush=True)
    
    response_line = input()
    response_obj = json.loads(response_line)
    return response_obj["pad_ok"]

def recover_block(target_block, prev_block):
    """Recover one plaintext block using padding oracle attack."""
    block_size = 16
    intermediate = bytearray(block_size)
    
    # Recover byte by byte from right to left
    for pad_len in range(1, block_size + 1):
        # We're looking for the byte at position (block_size - pad_len)
        target_pos = block_size - pad_len
        
        # Set up the forged previous block to produce the desired padding
        forged = bytearray(block_size)
        
        # Set already-known bytes to produce correct padding
        for i in range(target_pos + 1, block_size):
            forged[i] = intermediate[i] ^ pad_len
        
        # Brute force the current byte
        found = False
        for guess in range(256):
            forged[target_pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # Valid padding found
                # The intermediate byte is: guess XOR pad_len
                intermediate[target_pos] = guess ^ pad_len
                found = True
                break
        
        if not found:
            # Fallback: sometimes byte 0x01 is already valid and we need special handling
            # Try to verify by changing another byte
            if pad_len == 1:
                # Change the previous byte to ensure we don't have accidental longer padding
                for guess in range(256):
                    forged[target_pos] = guess
                    forged[target_pos - 1] = 0xFF  # Ensure different from what would give valid padding
                    
                    if padding_oracle(bytes(forged), target_block):
                        intermediate[target_pos] = guess ^ pad_len
                        found = True
                        break
            
            if not found:
                raise Exception(f"Failed to find valid padding at position {target_pos}")
    
    # XOR intermediate with actual previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(block_size))
    return plaintext

def main():
    start_time = time.monotonic_ns()
    
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
    
    # For first block, use IV as previous
    prev_block = iv_bytes
    
    for i, ct_block in enumerate(ct_blocks):
        recovered = recover_block(ct_block, prev_block)
        plaintext_blocks.append(recovered)
        prev_block = ct_block  # Current ciphertext block becomes prev for next
    
    # Concatenate all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    
    end_time = time.monotonic_ns()
    opspan = end_time - start_time
    
    # Output claim
    claim = {"plaintext_hex": full_plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{opspan}")

if __name__ == "__main__":
    main()