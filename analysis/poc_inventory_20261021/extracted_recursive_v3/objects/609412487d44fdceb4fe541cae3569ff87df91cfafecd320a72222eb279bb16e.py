#!/usr/bin/env python3
import sys
import json
import base64
import time

def padding_oracle(ct_base64):
    """Query the padding oracle with a ciphertext (at least 32 bytes)."""
    query = {"q": ct_base64}
    print(json.dumps(query), flush=True)
    response = json.loads(sys.stdin.readline())
    return response["pad_ok"]

def decrypt_block(oracle, prev_block, ct_block):
    """
    Decrypt a single 16-byte ciphertext block using a padding oracle.
    prev_block: the previous ciphertext block (or IV)
    ct_block: the current ciphertext block to decrypt
    Returns: 16-byte plaintext
    """
    # Intermediate state after block cipher decryption (before XOR with prev)
    intermediate = bytearray(16)
    
    # We'll build up the plaintext from right to left
    for pad_value in range(1, 17):
        pos = 16 - pad_value  # position we're attacking (15, 14, 13, ...)
        
        # Build a forged previous block
        forged = bytearray(16)
        
        # Set known bytes to produce the desired padding
        for i in range(pos + 1, 16):
            forged[i] = intermediate[i] ^ pad_value
        
        # Try all possible values for the unknown byte
        found = False
        candidates = []
        
        for guess in range(256):
            forged[pos] = guess
            
            # Query the oracle
            test_ct = bytes(forged) + ct_block
            if oracle(base64.b64encode(test_ct).decode()):
                candidates.append(guess)
        
        # Handle multiple candidates
        if len(candidates) == 0:
            raise ValueError(f"Failed to find byte at position {pos}")
        
        # If we have multiple candidates, we need to disambiguate
        if len(candidates) > 1 and pad_value == 1:
            # This happens when the original padding is \x01 or longer
            # We need to check which candidate is correct by changing the previous byte
            true_candidates = []
            for guess in candidates:
                # Set the current byte
                forged[pos] = guess
                # Change the previous byte to invalidate padding length 1
                if pos > 0:
                    forged[pos - 1] = forged[pos - 1] ^ 0xFF
                    test_ct = bytes(forged) + ct_block
                    if oracle(base64.b64encode(test_ct).decode()):
                        # This candidate still gives valid padding, so original padding > 1
                        true_candidates.append(guess)
                    forged[pos - 1] = forged[pos - 1] ^ 0xFF  # restore
                else:
                    # Can't disambiguate at position 0, just take first
                    true_candidates.append(guess)
                    break
            
            if len(true_candidates) == 1:
                candidates = true_candidates
            elif len(true_candidates) == 0:
                # None passed the test, so the original padding was exactly \x01
                # The correct candidate is the one where intermediate[pos] = 0x01
                # We need to find which guess gives us intermediate = 0x01
                # Since we're testing with pad_value = 1, forged[pos] = intermediate[pos] ^ 1
                # So intermediate[pos] = forged[pos] ^ 1
                # We want intermediate[pos] = 1, so forged[pos] = 0
                candidates = [c for c in candidates if (c ^ 1) == 1]
                if len(candidates) != 1:
                    # Just take the first one
                    candidates = candidates[:1]
        
        # Take the first candidate (or the disambiguated one)
        intermediate[pos] = candidates[0] ^ pad_value
    
    # Recover plaintext by XORing intermediate with previous block
    plaintext = bytes(intermediate[i] ^ prev_block[i] for i in range(16))
    return plaintext

def main():
    start_ns = time.monotonic_ns()
    
    # Read task instance
    with open(sys.argv[1], 'r') as f:
        task = json.load(f)
    
    public_input = task['public_input']
    ct_hex = public_input['ct_hex']
    iv_hex = public_input['iv_hex']
    
    # Parse ciphertext and IV
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    # Split ciphertext into 16-byte blocks
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    
    # Decrypt each block
    plaintext = b''
    prev = iv
    
    for block in blocks:
        pt_block = decrypt_block(padding_oracle, prev, block)
        plaintext += pt_block
        prev = block
    
    end_ns = time.monotonic_ns()
    
    # Output the claim
    claim = {"plaintext_hex": plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end_ns - start_ns}")

if __name__ == "__main__":
    main()