import sys
import json
import base64
import time
ct_hex = '2d8b1cf4a1462301d00db3524eaf30099264d96a23b7c2bd66715a3f32a6fcc4605c8bb0295d378dc2a41302274f62053bfa614a884a4dd598ca28fc61ee743f52bb56f89ad884d9238b15549ee55a28'
iv_hex = '2ceef434f762d4c6ba315182c44368df'
def oracle(prev, tgt):
    payload = base64.b64encode(prev + tgt).decode()
    print(json.dumps({'q': payload}), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError('eof')
    obj = json.loads(line)
    return obj['pad_ok'] is True
def decrypt_block(tgt):
    inter = bytearray(16)
    forged = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        for j in range(pos + 1, 16):
            forged[j] = inter[j] ^ pad
        found = None
        for guess in range(256):
            forged[pos] = guess
            ok = oracle(bytes(forged), tgt)
            if ok:
                if pad == 1:
                    forged[14] ^= 1
                    ok2 = oracle(bytes(forged), tgt)
                    forged[14] ^= 1
                    if not ok2:
                        continue
                found = guess
                break
        if found is None:
            raise RuntimeError('nofound')
        inter[pos] = found ^ pad
    return bytes(inter)
def main():
    t0 = time.monotonic_ns()
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
    blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
    prevs = [iv] + blocks[:-1]
    inters = []
    for tgt in blocks:
        inters.append(decrypt_block(tgt))
    pt_padded = b''.join(bytes(a ^ b for a, b in zip(I, P)) for I, P in zip(inters, prevs))
    pad = pt_padded[-1]
    if 1 <= pad <= 16 and pt_padded[-pad:] == bytes([pad]) * pad:
        pt = pt_padded[:-pad]
    else:
        pt = pt_padded
    t1 = time.monotonic_ns()
    print(f'OPSPAN_NS:{t1-t0}', flush=True)
    d = {'plaintext_hex': pt.hex()}
    print(f'CLAIM:{json.dumps(d)}', flush=True)
if __name__ == '__main__':
    main()