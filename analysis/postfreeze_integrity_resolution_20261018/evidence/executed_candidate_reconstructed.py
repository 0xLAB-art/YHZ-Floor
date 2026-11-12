#!/usr/bin/env python3
"""CBC PKCS#7 padding-oracle client. Reads an instance JSON (ct_hex, iv_hex),
queries the line-based oracle {"q": b64(forged_prev||target)} -> {"pad_ok":bool},
and emits CLAIM:{"plaintext_hex": ...}. Uses only the public ct/iv."""
import sys, json, base64

def oracle_ok(forged_prev, target_block):
    payload = base64.b64encode(bytes(forged_prev) + bytes(target_block)).decode()
    print(json.dumps({"q": payload}, separators=(",", ":")), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise SystemExit(1)
    try:
        resp = json.loads(line)
    except ValueError:
        raise SystemExit(1)
    return bool(resp.get("pad_ok"))

def recover_dec(target):
    """Recover raw CBC decryption D(target) for one 16-byte block."""
    dec = bytearray(16)
    # --- byte 15: find forge making final pad byte 0x01, disambiguating longer pads ---
    last = None
    for x in range(256):
        probe = bytearray(16)
        probe[15] = x
        if not oracle_ok(probe, target):
            continue
        last = x
        probe[14] = 0xAA  # different second-to-last byte keeps a true 0x01 pad valid,
        if oracle_ok(probe, target):  # but invalidates any accidental longer pad
            dec[15] = x ^ 0x01
            last = None
            break
    if last is not None:
        dec[15] = last ^ 0x01
    # --- bytes 14..0: force the known pad suffix, then hunt the matching forge byte ---
    for i in range(14, -1, -1):
        pad = 16 - i
        probe = bytearray(16)
        for j in range(i + 1, 16):
            probe[j] = dec[j] ^ pad  # makes plaintext[j] == pad
        for x in range(256):
            probe[i] = x
            if oracle_ok(probe, target):
                dec[i] = x ^ pad
                break
        else:
            raise SystemExit(2)  # no valid forge found: oracle contract violated
    return bytes(dec)

def main():
    with open(sys.argv[1], "r") as fh:
        inst = json.load(fh)
    ct = bytes.fromhex(inst["ct_hex"])
    iv = bytes.fromhex(inst["iv_hex"])
    blocks = [ct[k:k + 16] for k in range(0, len(ct), 16)]
    plain = bytearray()
    for k, block in enumerate(blocks):
        prev = iv if k == 0 else blocks[k - 1]
        dec = recover_dec(block)
        plain.extend(dec[i] ^ prev[i] for i in range(16))
    n = len(plain)
    if n and 1 <= plain[-1] <= 16 and plain[-plain[-1]:] == bytes([plain[-1]]) * plain[-1]:
        plain = plain[:-plain[-1]]  # strip valid PKCS#7 padding
    print("CLAIM:" + json.dumps({"plaintext_hex": plain.hex()}, separators=(",", ":")), flush=True)

main()
