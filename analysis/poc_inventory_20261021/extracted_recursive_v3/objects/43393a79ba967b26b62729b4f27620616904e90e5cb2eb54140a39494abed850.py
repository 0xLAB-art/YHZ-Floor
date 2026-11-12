import json
import base64
import sys
from time import monotonic_ns

def main():
    # Parse provisioned material
    ct_hex = "39938ac88f5963d8634a6f1ecf28a57b700c1478db86129cd1a329de524260c554df20ef1a199e7a2287636b1e9453d89a0f051426c4238867573c7e09fc046632e08204ad00fa2d53d6f18d4a947b2b"
    iv_hex = "3748e1aa7b75534a6b3e482db2c19dfc"
    
    # Convert to bytes
    iv = bytes.fromhex(iv_hex)
    ct = bytes.fromhex(ct_hex)
    
    # Split ciphertext into blocks (first block is IV, then 4 data blocks)
    blocks = [iv] + [ct[i:i+16] for i in range(0, len(ct), 16)]
    num_blocks = len(blocks) - 1  # Number of data blocks (4)
    
    # Store decrypted plaintext blocks
    plaintext_blocks = []
    
    # For each block from last to first
    for block_idx in range(num_blocks, 0, -1):
        # Target block is blocks[block_idx]
        target_block = blocks[block_idx]
        # Previous block (will be forged)
        prev_block = blocks[block_idx-1]
        
        # Initialize intermediate state and decrypted block
        intermediate = bytearray(16)
        decrypted_block = bytearray(16)
        
        # For each byte from last to first in the block
        for byte_idx in range(15, -1, -1):
            # Padding value for this round
            pad_val = 16 - byte_idx
            
            # Create forged previous block
            forged_prev = bytearray(16)
            
            # Set bytes after current index to known intermediate XOR desired padding
            for j in range(15, byte_idx, -1):
                forged_prev[j] = intermediate[j] ^ pad_val
            
            # Try all possible values for current byte
            found = False
            for guess in range(256):
                forged_prev[byte_idx] = guess
                
                # Create query: forged_prev || target_block
                query = bytes(forged_prev) + target_block
                query_b64 = base64.b64encode(query).decode('ascii')
                
                # Send query to oracle
                print(json.dumps({"q": query_b64}))
                sys.stdout.flush()
                
                # Read response
                response = sys.stdin.readline().strip()
                if not response:
                    continue
                oracle_response = json.loads(response)
                
                if oracle_response.get("pad_ok", False):
                    # Valid padding found
                    intermediate[byte_idx] = guess ^ pad_val
                    decrypted_block[byte_idx] = intermediate[byte_idx] ^ prev_block[byte_idx]
                    found = True
                    break
            
            if not found:
                # Should not happen if oracle is correct
                raise Exception("No valid padding found for byte")
        
        plaintext_blocks.insert(0, decrypted_block)
    
    # Combine all plaintext blocks
    plaintext = b''.join(plaintext_blocks)
    
    # Remove PKCS#7 padding
    pad_len = plaintext[-1]
    if pad_len <= 16:
        plaintext = plaintext[:-pad_len]
    
    # Output claim
    claim = {"plaintext_hex": plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()