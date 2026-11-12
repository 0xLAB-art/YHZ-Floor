import base64
import json
import sys
import time

def query_oracle(forged_prev: bytes, target_block: bytes) -> bool:
    query = forged_prev + target_block
    q_b64 = base64.b64encode(query).decode()
    sys.stdout.write('{"q":"' + q_b64 + '"}\n')
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise EOFError("No response from oracle")
    data = json.loads(line.strip())
    return data.get("pad_ok", False)

def decrypt_block(target_block: bytes, real_prev: bytes) -> bytes:
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
                    second = None
                    for g2 in range(guess + 1, 256):
                        forged_prev[pos] = g2
                        if query_oracle(bytes(forged_prev), target_block):
                            second = g2
                            break
                    if second is not None:
                        orig = forged_prev[14]
                        forged_prev[14] ^= 1
                        forged_prev[pos] = candidate
                        if not query_oracle(bytes(forged_prev), target_block):
                            guess = candidate
                        else:
                            guess = second
                        forged_prev[14] = orig
                D[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            raise ValueError(f"Failed at pos {pos}")
    return bytes(d ^ rp for d, rp in zip(D, real_prev))

def main():
    start = time.monotonic_ns()
    ct = bytes.fromhex("3901eaefdb0e89e52c39bf37208de1cf168554a9cd70d9ae1276eb730bc0ba967a9e97661bfc886e4d0cfbfd1dab1e79428cf9bd9b409bce2d621b7909d2dd2cc0134b5e115448afd23fa199544879b4")
    iv = bytes.fromhex("3228e5d15a021704f1e9ff82243c2ec3")
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    plaintext = bytearray()
    prev = iv
    for blk in blocks:
        pt = decrypt_block(blk, prev)
        plaintext.extend(pt)
        prev = blk
    pad = plaintext[-1]
    if 1 <= pad <= 16 and all(b == pad for b in plaintext[-pad:]):
        plaintext = plaintext[:-pad]
    end = time.monotonic_ns()
    sys.stdout.write('CLAIM:{"plaintext_hex":"' + plaintext.hex() + '"}\n')
    sys.stdout.write(f'OPSPAN_NS:{end - start}\n')
    sys.stdout.flush()

if __name__ == "__main__":
    main()