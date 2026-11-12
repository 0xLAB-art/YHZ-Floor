import sys, base64, time, json

def read_response():
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

def query(forged_prev, target):
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    # print JSON without spaces as required by the verifier
    sys.stdout.write('{"q":"' + b64 + '"}\n')
    sys.stdout.flush()
    resp = read_response()
    return resp.get('pad_ok', False)

def recover_intermediate(target, block_size=16):
    I = bytearray(block_size)
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        prefix = bytearray(block_size)
        for j in range(pos+1, block_size):
            prefix[j] = I[j] ^ pad_val
        for guess in range(256):
            forged = bytearray(prefix)
            forged[pos] = guess
            if query(forged, target):
                I[pos] = guess ^ pad_val
                break
        else:
            raise Exception('Failed to recover byte at position {}'.format(pos))
    return bytes(I)

def main():
    # provisioned data from task description
    ct_hex = "c7711bdd7a8f67ed922f24fc47d82773a74ec4e22b956b8d136f111f9b06957d147c4a5c34b7a9915dcc9ed713761c0bf307d61ebc42f30fff02c6fc26db64f6ca9de52439ed691a16c07f0288c6f8cd"
    iv_hex = "09ea8825545288faceb05eef36757481"
    block_size = 16
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]
    plaintext = bytearray()
    start = time.monotonic_ns()
    for idx, target in enumerate(blocks):
        prev = iv if idx == 0 else blocks[idx-1]
        intermediate = recover_intermediate(target, block_size)
        pblock = bytes(a ^ b for a, b in zip(intermediate, prev))
        plaintext.extend(pblock)
    end = time.monotonic_ns()
    # Output timing (optional) then final claim
    sys.stdout.write(f"OPSPAN_NS:{end - start}\n")
    sys.stdout.write(f"CLAIM:{json.dumps({'plaintext_hex': plaintext.hex()})}\n")
    sys.stdout.flush()

if __name__ == '__main__':
    main()