#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev, target_block):
    """Query the padding oracle with forged_prev || target_block."""
    query_bytes = forged_prev + target_block
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    query_json = json.dumps({"q": query_b64})
    print(query_json, flush=True)
    
    response_line = sys.stdin.readline().strip()
    response = json.loads(response_line)
    return response["pad_ok"]

def recover_block(target_block, prev_block):
    """Recover one plaintext block using padding oracle."""
    decrypted = bytearray(16)
    
    # For each byte position from right to left
    for pad_len in range(1, 17):
        pos = 16 - pad_len
        
        # Set up the forged block to produce the desired padding
        forged = bytearray(16)
        for i in range(pos + 1, 16):
            forged[i] = decrypted[i] ^ pad_len
        
        # Brute force the current byte
        found = False
        for guess in range(256):
            forged[pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # Padding is valid
                # Check if this is a false positive (when we're looking for pad=1)
                if pad_len == 1 and guess == forged[pos]:
                    # Verify by flipping the second-to-last byte
                    test_forged = forged.copy()
                    test_forged[14] ^= 1
                    if padding_oracle(bytes(test_forged), target_block):
                        # Still valid, so we actually have pad >= 2, not pad = 1
                        continue
                
                # Valid padding found
                decrypted[pos] = guess ^ pad_len
                found = True
                break
        
        if not found:
            raise ValueError(f"Failed to find valid padding at position {pos}")
    
    # XOR with actual previous block to get plaintext
    plaintext = bytes(decrypted[i] ^ prev_block[i] for i in range(16))
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
    ciphertext = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into blocks
    block_size = 16
    num_blocks = len(ciphertext) // block_size
    ct_blocks = [ciphertext[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    # Recover each block
    plaintext_blocks = []
    
    # First block uses IV as previous
    prev = iv
    for i, ct_block in enumerate(ct_blocks):
        recovered = recover_block(ct_block, prev)
        plaintext_blocks.append(recovered)
        prev = ct_block
    
    # Combine plaintext
    full_plaintext = b''.join(plaintext_blocks)
    
    end_time = time.monotonic_ns()
    opspan = end_time - start_time
    
    # Output results
    plaintext_hex = full_plaintext.hex()
    claim = {"plaintext_hex": plaintext_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{opspan}")

if __name__ == "__main__":
    main()