#!/usr/bin/env python3
import sys
import json
import base64
import time

def query_oracle(forged_prev: bytes, target_block: bytes) -> bool:
    """Query the padding oracle with forged_prev || target_block."""
    query_bytes = forged_prev + target_block
    query_b64 = base64.b64encode(query_bytes).decode('ascii')
    query_msg = json.dumps({"q": query_b64})
    print(query_msg, flush=True)
    
    reply_line = sys.stdin.readline().strip()
    reply = json.loads(reply_line)
    return reply["pad_ok"]

def recover_block(target_block: bytes, prev_block: bytes) -> bytes:
    """Recover a single 16-byte plaintext block using padding oracle."""
    plaintext = bytearray(16)
    intermediate = bytearray(16)
    
    # Recover byte by byte from right to left
    for pos in range(15, -1, -1):
        padding_value = 16 - pos
        
        # Build forged block that will produce the desired padding
        forged = bytearray(16)
        
        # Set known bytes to produce correct padding
        for i in range(pos + 1, 16):
            forged[i] = intermediate[i] ^ padding_value
        
        # Try all possible values for current byte
        found = False
        for guess in range(256):
            forged[pos] = guess
            
            if query_oracle(bytes(forged), target_block):
                # Potential hit - but we need to verify it's not a false positive
                # A false positive occurs when we accidentally create valid padding
                # of length > padding_value (e.g., we want \x01 but get \x02\x02)
                
                if padding_value == 1:
                    # For padding_value=1, verify by flipping the previous byte
                    # If it's truly \x01, changing prev byte should break padding
                    if pos > 0:
                        test_forged = bytearray(forged)
                        test_forged[pos - 1] ^= 0x01
                        if not query_oracle(bytes(test_forged), target_block):
                            # Confirmed: this is real \x01 padding
                            intermediate[pos] = guess ^ padding_value
                            plaintext[pos] = intermediate[pos] ^ prev_block[pos]
                            found = True
                            break
                    else:
                        # pos == 0, can't verify but likely correct
                        intermediate[pos] = guess ^ padding_value
                        plaintext[pos] = intermediate[pos] ^ prev_block[pos]
                        found = True
                        break
                else:
                    # For padding_value > 1, accept first valid response
                    intermediate[pos] = guess ^ padding_value
                    plaintext[pos] = intermediate[pos] ^ prev_block[pos]
                    found = True
                    break
        
        if not found:
            raise ValueError(f"Failed to find valid padding at position {pos}")
    
    return bytes(plaintext)

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
    
    # Split ciphertext into 16-byte blocks
    blocks = []
    for i in range(0, len(ct_bytes), 16):
        blocks.append(ct_bytes[i:i+16])
    
    # Recover plaintext block by block
    plaintext_blocks = []
    
    # First block uses IV as previous
    prev = iv_bytes
    for block in blocks:
        recovered = recover_block(block, prev)
        plaintext_blocks.append(recovered)
        prev = block
    
    # Concatenate all plaintext blocks
    full_plaintext = b''.join(plaintext_blocks)
    
    end_time = time.monotonic_ns()
    duration = end_time - start_time
    
    # Output claim
    claim = {"plaintext_hex": full_plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{duration}")

if __name__ == "__main__":
    main()