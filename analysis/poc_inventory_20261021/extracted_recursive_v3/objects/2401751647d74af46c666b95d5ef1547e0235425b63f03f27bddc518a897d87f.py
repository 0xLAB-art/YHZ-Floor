#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev: bytes, target: bytes) -> bool:
    """Query the padding oracle with forged_prev || target."""
    query = forged_prev + target
    query_b64 = base64.b64encode(query).decode('ascii')
    print(json.dumps({"q": query_b64}), flush=True)
    
    response_line = sys.stdin.readline().strip()
    response = json.loads(response_line)
    return response["pad_ok"]

def decrypt_block(oracle_func, prev_block: bytes, target_block: bytes) -> bytes:
    """Decrypt a single block using padding oracle attack."""
    intermediate = bytearray(16)
    
    # Recover each byte from right to left
    for pad_value in range(1, 17):
        # Set up the padding for already-known bytes
        forged = bytearray(16)
        for i in range(16 - pad_value + 1, 16):
            forged[i] = intermediate[i] ^ pad_value
        
        # Brute force the current byte
        found = False
        for guess in range(256):
            forged[16 - pad_value] = guess
            
            if oracle_func(bytes(forged), target_block):
                # Verify this is not a false positive (except for pad_value=1)
                if pad_value == 1:
                    # Test if we accidentally hit valid 0x0202 instead of 0x01
                    if 16 - pad_value - 1 >= 0:
                        test_forged = forged.copy()
                        test_forged[16 - pad_value - 1] ^= 1
                        if oracle_func(bytes(test_forged), target_block):
                            # This is actually 0x0202, not 0x01
                            continue
                
                intermediate[16 - pad_value] = guess ^ pad_value
                found = True
                break
        
        if not found:
            raise ValueError(f"Failed to find byte at position {16 - pad_value}")
    
    # XOR intermediate with previous block to get plaintext
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
    ciphertext = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into blocks
    block_size = 16
    num_blocks = len(ciphertext) // block_size
    ct_blocks = [ciphertext[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    # Decrypt each block
    plaintext_blocks = []
    prev_block = iv
    
    for i, ct_block in enumerate(ct_blocks):
        pt_block = decrypt_block(padding_oracle, prev_block, ct_block)
        plaintext_blocks.append(pt_block)
        prev_block = ct_block
    
    # Concatenate plaintext
    full_plaintext = b''.join(plaintext_blocks)
    
    # Remove PKCS#7 padding
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= 16:
        # Verify padding is valid
        if all(b == pad_len for b in full_plaintext[-pad_len:]):
            plaintext = full_plaintext[:-pad_len]
        else:
            plaintext = full_plaintext
    else:
        plaintext = full_plaintext
    
    end_time = time.monotonic_ns()
    
    # Output results
    print(f"OPSPAN_NS:{end_time - start_time}")
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext.hex()})}")

if __name__ == "__main__":
    main()