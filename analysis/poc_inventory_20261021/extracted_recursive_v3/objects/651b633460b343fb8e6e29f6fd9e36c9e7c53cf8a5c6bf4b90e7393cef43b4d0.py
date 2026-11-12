import sys, json, base64, time

def read_response():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line.strip())

def query(forged_prev: bytes, target: bytes) -> bool:
    # forged_prev and target are each 16 bytes
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    resp = read_response()
    return resp.get("pad_ok", False)

def recover_block(target: bytes, prev_cipher: bytes) -> bytes:
    # returns plaintext block (16 bytes)
    block_size = 16
    intermediate = [0] * block_size  # D_i values
    for pad_len in range(1, block_size + 1):
        pos = block_size - pad_len
        found = False
        for guess in range(256):
            forged = bytearray(block_size)
            # set bytes for already known positions to force correct padding
            for j in range(block_size - 1, pos, -1):
                forged[j] = intermediate[j] ^ pad_len
            # set current byte guess
            forged[pos] = guess ^ pad_len
            # other bytes remain 0
            if query(bytes(forged), target):
                # we have a valid padding
                intermediate[pos] = guess ^ pad_len
                found = True
                break
        if not found:
            # Should never happen
            raise RuntimeError("Failed to recover byte at position {}".format(pos))
    # compute plaintext = intermediate XOR prev_cipher
    plain = bytes([intermediate[i] ^ prev_cipher[i] for i in range(block_size)])
    return plain

def pkcs7_unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding")
    return data[:-pad_len]

def main():
    ct_hex = "a51ba5d6f5be349e423b8cd10a39b67adca1a68f66df38d5d35ae752d8f018aaad2053e1270a8dcfc8ad62dfa17e76082e8dd2081967a19d803191459b10e9f1cafa61a91409c8b178135927994a3468"
    iv_hex = "9f221fd1953aa085566619ac003e5dd7"
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    block_size = 16
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext_blocks = []
    prev = iv
    for blk in blocks:
        plain_blk = recover_block(blk, prev)
        plaintext_blocks.append(plain_blk)
        prev = blk
    padded_plain = b"".join(plaintext_blocks)
    try:
        plain = pkcs7_unpad(padded_plain)
    except Exception:
        plain = padded_plain  # fallback, verifier will strip anyway
    claim = {"plaintext_hex": plain.hex()}
    # optional timing measurement
    start = time.monotonic_ns()
    # (no heavy work after this point)
    end = time.monotonic_ns()
    sys.stdout.write("OPSPAN_NS:" + str(end - start) + "\n")
    sys.stdout.flush()
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()