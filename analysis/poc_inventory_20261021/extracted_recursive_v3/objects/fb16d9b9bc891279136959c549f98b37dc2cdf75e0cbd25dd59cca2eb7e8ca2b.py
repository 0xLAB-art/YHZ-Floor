#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(forged_prev, target_block):
    """Query the padding oracle with forged_prev || target_block."""
    query = forged_prev + target_block
    query_b64 = base64.b64encode(query).decode('ascii')
    print(json.dumps({"q": query_b64}), flush=True)
    response = json.loads(sys.stdin.readline())
    return response["pad_ok"]

def decrypt_block(target_block, prev_block):
    """Decrypt a single 16-byte block using the padding oracle."""
    intermediate = bytearray(16)
    
    for pad_len in range(1, 17):
        target_pos = 16 - pad_len
        
        forged = bytearray(16)
        
        # Set known bytes to produce the desired padding
        for i in range(target_pos + 1, 16):
            forged[i] = intermediate[i] ^ pad_len
        
        # Brute force the target byte
        found = False
        for guess in range(256):
            forged[target_pos] = guess
            
            if padding_oracle(bytes(forged), target_block):
                # For pad_len == 1, verify it's not accidentally matching longer padding
                if pad_len == 1:
                    # Change another byte to verify we have true 0x01 padding
                    test_forged = bytearray(forged)
                    test_forged[14] ^= 1
                    if not padding_oracle(bytes(test_forged), target_block):
                        # This confirms we found the right byte
                        intermediate[target_pos] = guess ^ pad_len
                        found = True
                        break
                else:
                    # For longer padding, finding valid padding is sufficient
                    intermediate[target_pos] = guess ^ pad_len
                    found = True
                    break
        
        if not found:
            raise Exception(f"Failed to find byte at position {target_pos}")
    
    # XOR intermediate state with actual previous block to get plaintext
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    start_time = time.monotonic_ns()
    
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    ct_bytes = bytes.fromhex(task['public_input']['ct_hex'])
    iv = bytes.fromhex(task['public_input']['iv_hex'])
    
    # Split ciphertext into 16-byte blocks
    blocks = [ct_bytes[i:i+16] for i in range(0, len(ct_bytes), 16)]
    
    # Decrypt each block
    plaintext_blocks = []
    
    prev = iv
    for block in blocks:
        pt_block = decrypt_block(block, prev)
        plaintext_blocks.append(pt_block)
        prev = block
    
    # Concatenate all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    
    # Remove PKCS#7 padding
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= 16:
        if all(b == pad_len for b in full_plaintext[-pad_len:]):
            plaintext_unpadded = full_plaintext[:-pad_len]
        else:
            plaintext_unpadded = full_plaintext
    else:
        plaintext_unpadded = full_plaintext
    
    end_time = time.monotonic_ns()
    
    print(f"OPSPAN_NS:{end_time - start_time}")
    print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_unpadded.hex()})}")

if __name__ == '__main__':
    main()