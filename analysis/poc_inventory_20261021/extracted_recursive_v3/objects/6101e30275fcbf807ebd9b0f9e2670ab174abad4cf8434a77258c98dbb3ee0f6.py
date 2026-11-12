#!/usr/bin/env python3
import sys
import json
import base64
import time

def query_oracle(forged_prev, target_block):
    """Query the padding oracle with forged_prev || target_block."""
    query_bytes = forged_prev + target_block
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    query_json = json.dumps({"q": query_b64})
    print(query_json, flush=True)
    
    response_line = sys.stdin.readline().strip()
    response = json.loads(response_line)
    return response["pad_ok"]

def recover_block(target_block, prev_block):
    """Recover one plaintext block using padding oracle attack."""
    # Intermediate state after block cipher decryption (before XOR with prev)
    intermediate = bytearray(16)
    
    # Work backwards from position 15 to 0
    for pos in range(15, -1, -1):
        padding_value = 16 - pos  # desired padding: 1, 2, 3, ..., 16
        
        # Prepare forged previous block
        forged = bytearray(16)
        
        # Set known bytes to produce correct padding
        for i in range(pos + 1, 16):
            forged[i] = intermediate[i] ^ padding_value
        
        # Try all possible byte values for current position
        found = False
        for guess in range(256):
            forged[pos] = guess
            
            if query_oracle(bytes(forged), target_block):
                # Valid padding found
                # The decrypted byte XOR guess = padding_value
                intermediate[pos] = guess ^ padding_value
                found = True
                break
        
        if not found:
            # Special case: when pos=15, if we get padding with the zero forged block,
            # we might already have valid padding. Try to distinguish.
            # However, this is rare. Let's handle it by trying pattern detection.
            
            # If we're at position 15 and nothing worked, the block might already
            # end in valid padding. Try to detect by checking if original causes pad_ok.
            if pos == 15:
                # Check with all-zero forged block
                if query_oracle(bytes(16), target_block):
                    # Already has valid padding with zero forged. 
                    # Try changing last byte to break it and find real value.
                    for guess in range(256):
                        forged_test = bytearray(16)
                        forged_test[15] = guess
                        if not query_oracle(bytes(forged_test), target_block):
                            # This breaks padding, so original must be guess ^ some_padding
                            # Try padding values 1-16
                            for pad_val in range(1, 17):
                                intermediate[15] = guess ^ pad_val
                                # Verify by trying to get padding=2
                                forged_verify = bytearray(16)
                                forged_verify[15] = intermediate[15] ^ 2
                                forged_verify[14] = intermediate[14] ^ 2 if pos < 14 else 0
                                # Actually we don't know intermediate[14] yet
                                # Let's use a different approach
                                found = True
                                break
                            if found:
                                break
                
                if not found:
                    raise ValueError(f"Failed to find valid padding at position {pos}")
            else:
                raise ValueError(f"Failed to find valid padding at position {pos}")
    
    # Recover plaintext by XORing intermediate with actual previous block
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
    
    ct_bytes = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into blocks
    block_size = 16
    num_blocks = len(ct_bytes) // block_size
    ct_blocks = [ct_bytes[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    start_time = time.monotonic_ns()
    
    # Recover each block
    plaintext_blocks = []
    for i in range(num_blocks):
        target_block = ct_blocks[i]
        prev_block = iv if i == 0 else ct_blocks[i-1]
        
        pt_block = recover_block(target_block, prev_block)
        plaintext_blocks.append(pt_block)
    
    end_time = time.monotonic_ns()
    
    # Concatenate all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    plaintext_hex = full_plaintext.hex()
    
    # Output timing
    print(f"OPSPAN_NS:{end_time - start_time}")
    
    # Output claim
    claim = {"plaintext_hex": plaintext_hex}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()