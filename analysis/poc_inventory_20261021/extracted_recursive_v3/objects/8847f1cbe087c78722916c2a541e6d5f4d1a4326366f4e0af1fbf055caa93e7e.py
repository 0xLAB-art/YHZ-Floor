import base64
import json
import sys
import time

def query_oracle(forged_prev: bytes, target_block: bytes) -> bool:
    """Send a padding oracle query and return the result."""
    query = forged_prev + target_block
    q_b64 = base64.b64encode(query).decode()
    print(json.dumps({"q": q_b64}), flush=True)
    sys.stdout.flush()
    response = sys.stdin.readline()
    if not response:
        raise EOFError("No response from oracle")
    result = json.loads(response.strip())
    return result.get("pad_ok", False)

def decrypt_block(target_block: bytes, real_prev: bytes) -> bytes:
    """Decrypt a single block using the padding oracle.
    Returns the plaintext block (16 bytes)."""
    D = bytearray(16)
    forged_prev = bytearray(16)
    
    for pad_len in range(1, 17):
        pos = 16 - pad_len
        
        for j in range(pos + 1, 16):
            forged_prev[j] = D[j] ^ pad_len
        
        found = False
        for guess in range(256):
            forged_prev[pos] = guess
            if query_oracle(bytes(forged_prev), target_block):
                if pad_len == 1:
                    candidate = guess
                    second_candidate = None
                    for g2 in range(guess + 1, 256):
                        forged_prev[pos] = g2
                        if query_oracle(bytes(forged_prev), target_block):
                            second_candidate = g2
                            break
                    if second_candidate is not None:
                        orig_14 = forged_prev[14]
                        forged_prev[14] ^= 1
                        forged_prev[pos] = candidate
                        if not query_oracle(bytes(forged_prev), target_block):
                            guess = candidate
                        else:
                            guess = second_candidate
                        forged_prev[14] = orig_14
                
                D[pos] = guess ^ pad_len
                found = True
                break
        
        if not found:
            raise ValueError(f"Failed to find byte at position {pos}")
    
    plaintext = bytes(d ^ rp for d, rp in zip(D, real_prev))
    return plaintext

def main():
    start_ns = time.monotonic_ns()
    
    ct_hex = "3901eaefdb0e89e52c39bf37208de1cf168554a9cd70d9ae1276eb730bc0ba967a9e97661bfc886e4d0cfbfd1dab1e79428cf9bd9b409bce2d621b7909d2dd2cc0134b5e115448afd23fa199544879b4"
    iv_hex = "3228e5d15a021704f1e9ff82243c2ec3"
    
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    
    block_size = 16
    num_blocks = len(ct) // block_size
    ciphertext_blocks = [ct[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
    
    plaintext_blocks = []
    prev_block = iv
    for i, block in enumerate(ciphertext_blocks):
        pt_block = decrypt_block(block, prev_block)
        plaintext_blocks.append(pt_block)
        prev_block = block
    
    full_plaintext = b''.join(plaintext_blocks)
    
    pad_len = full_plaintext[-1]
    if 1 <= pad_len <= 16:
        if all(b == pad_len for b in full_plaintext[-pad_len:]):
            full_plaintext = full_plaintext[:-pad_len]
    
    end_ns = time.monotonic_ns()
    
    claim = {"plaintext_hex": full_plaintext.hex()}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end_ns - start_ns}", flush=True)

if __name__ == "__main__":
    main()