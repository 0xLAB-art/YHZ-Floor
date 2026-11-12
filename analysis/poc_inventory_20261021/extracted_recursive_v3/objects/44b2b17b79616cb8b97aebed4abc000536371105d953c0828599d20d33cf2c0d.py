#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev, target_block):
    """Query the padding oracle with forged_prev || target_block."""
    query_bytes = forged_prev + target_block
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(sys.stdin.readline())
    return response["pad_ok"]

def recover_block(target_block, prev_block):
    """Recover one 16-byte plaintext block using padding oracle attack."""
    intermediate = bytearray(16)
    
    # Work backwards from byte 15 to byte 0
    for pad_val in range(1, 17):
        pos = 16 - pad_val
        
        # Prepare the forged previous block
        forged = bytearray(16)
        
        # Set known bytes to produce the target padding value
        for i in range(pos + 1, 16):
            forged[i] = intermediate[i] ^ pad_val
        
        # Brute force the current byte
        found = False
        for guess in range(256):
            forged[pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # Valid padding found
                # The intermediate value at this position is guess ^ pad_val
                intermediate[pos] = guess ^ pad_val
                
                # Verify it's not a false positive (when pad_val == 1)
                if pad_val == 1:
                    # Try changing the previous byte to ensure we have \x01 not \x02\x02
                    test_forged = bytearray(forged)
                    test_forged[pos - 1] ^= 1
                    if not padding_oracle(bytes(test_forged), target_block):
                        # This was indeed \x01, not longer padding
                        found = True
                        break
                    # Otherwise it's \x02\x02 or longer, keep searching
                else:
                    found = True
                    break
        
        if not found:
            raise ValueError(f"Failed to find valid padding at position {pos}")
    
    # XOR intermediate with actual previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    start_ns = time.monotonic_ns()
    
    # Read the task instance
    instance_path = sys.argv[1]
    with open(instance_path, 'r') as f:
        instance = json.load(f)
    
    public_input = instance["public_input"]
    ct_hex = public_input["ct_hex"]
    iv_hex = public_input["iv_hex"]
    
    # Parse ciphertext and IV
    ct_bytes = bytes.fromhex(ct_hex)
    iv_bytes = bytes.fromhex(iv_hex)
    
    # Split ciphertext into blocks
    block_size = 16
    num_blocks = len(ct_bytes) // block_size
    ct_blocks = [ct_bytes[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    # Recover each block
    plaintext_blocks = []
    prev_block = iv_bytes
    
    for i, ct_block in enumerate(ct_blocks):
        pt_block = recover_block(ct_block, prev_block)
        plaintext_blocks.append(pt_block)
        prev_block = ct_block
    
    # Concatenate all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    
    end_ns = time.monotonic_ns()
    
    # Output the claim
    claim = {"plaintext_hex": full_plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end_ns - start_ns}")

if __name__ == "__main__":
    main()