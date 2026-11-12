#!/usr/bin/env python3
import sys
import json
import base64
import time

def query_oracle(forged_prev: bytes, target_block: bytes) -> bool:
    """Query the padding oracle with two blocks."""
    query_bytes = forged_prev + target_block
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    
    query_obj = {"q": query_b64}
    print(json.dumps(query_obj), flush=True)
    
    response_line = sys.stdin.readline().strip()
    response_obj = json.loads(response_line)
    return response_obj["pad_ok"]

def recover_block(target_block: bytes, prev_block: bytes) -> bytes:
    """Recover one plaintext block using padding oracle attack."""
    intermediate = bytearray(16)
    
    # Recover byte by byte from right to left
    for pos in range(15, -1, -1):
        padding_value = 16 - pos
        
        # Construct forged previous block
        forged = bytearray(16)
        
        # Set known bytes to produce correct padding
        for i in range(pos + 1, 16):
            forged[i] = intermediate[i] ^ padding_value
        
        # Try all possible values for current byte
        found = False
        for guess in range(256):
            forged[pos] = guess
            
            if query_oracle(bytes(forged), target_block):
                # Found valid padding
                # The intermediate value at this position
                candidate = guess ^ padding_value
                intermediate[pos] = candidate
                
                # Validate: if pos == 15, ensure it's not a false positive
                # by checking if changing another byte breaks padding
                if pos == 15:
                    # Try changing the second-to-last byte
                    test_forged = bytearray(forged)
                    test_forged[14] ^= 1
                    if not query_oracle(bytes(test_forged), target_block):
                        # Good, this is the real \x01 padding
                        found = True
                        break
                    # Otherwise, this might be \x02\x02 or longer padding
                    # The guess is still valid, intermediate[15] = guess ^ 1
                    # But we need to verify
                    # Actually, for simplicity, let's accept the first valid one
                    # and handle edge cases differently
                else:
                    found = True
                    break
        
        if not found and pos == 15:
            # Special handling for last byte - try all values again
            # looking for natural padding
            for guess in range(256):
                forged[pos] = guess
                if query_oracle(bytes(forged), target_block):
                    intermediate[pos] = guess ^ 1
                    found = True
                    break
        
        if not found:
            raise ValueError(f"Failed to find valid padding at position {pos}")
    
    # XOR intermediate with actual previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
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
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into blocks
    block_size = 16
    num_blocks = len(ct) // block_size
    ct_blocks = [ct[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    # Recover each block
    plaintext_blocks = []
    
    # First block uses IV as previous
    prev = iv
    for i, ct_block in enumerate(ct_blocks):
        recovered = recover_block(ct_block, prev)
        plaintext_blocks.append(recovered)
        prev = ct_block
    
    # Concatenate all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    
    end_time = time.monotonic_ns()
    
    # Output claim
    claim = {"plaintext_hex": full_plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end_time - start_time}")

if __name__ == "__main__":
    main()