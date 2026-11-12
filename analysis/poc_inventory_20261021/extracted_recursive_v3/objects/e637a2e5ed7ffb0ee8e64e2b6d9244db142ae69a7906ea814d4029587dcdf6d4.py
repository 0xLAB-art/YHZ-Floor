import base64
import binascii
import json
import sys


N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551


def instance():
    if len(sys.argv) != 2:
        raise SystemExit("missing instance path")
    with open(sys.argv[1]) as f:
        value = json.load(f)
    if value.get("schema_version") != "agent-instance-v3":
        raise SystemExit("wrong instance schema")
    return value["condition"], value["public_input"]


def xor_hex(left, right):
    return bytes(a ^ b for a, b in zip(bytes.fromhex(left), bytes.fromhex(right)))


def ecdsa(p):
    r1 = int(p["sig1_hex"][:64], 16)
    s1 = int(p["sig1_hex"][64:], 16)
    r2 = int(p["sig2_hex"][:64], 16)
    s2 = int(p["sig2_hex"][64:], 16)
    if r1 != r2 or s1 == s2:
        raise SystemExit("invalid repeated-nonce instance")
    z1 = int(p["z1_hex"], 16)
    z2 = int(p["z2_hex"], 16)
    k = ((z1 - z2) * pow(s1 - s2, -1, N)) % N
    d = ((s1 * k - z1) * pow(r1, -1, N)) % N
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import ECC
    from Crypto.Signature import DSS
    key = ECC.construct(curve="NIST P-256", d=d)
    signature = DSS.new(key, "fips-186-3").sign(
        SHA256.new(bytes.fromhex(p["challenge_msg_hex"])))
    return {"d_hex": f"{d:064x}", "sig_hex": signature.hex()}


def cbc(p):
    blocks = [bytes.fromhex(p["ct_hex"])[i:i + 16] for i in range(0, len(bytes.fromhex(p["ct_hex"])), 16)]
    iv = bytes.fromhex(p["iv_hex"])
    plaintext = []
    for index, target in enumerate(blocks):
        original = iv if index == 0 else blocks[index - 1]
        intermediate = [0] * 16
        for position in range(15, -1, -1):
            padding = 16 - position
            forged = bytearray(16)
            for j in range(position + 1, 16):
                forged[j] = intermediate[j] ^ padding
            found = None
            for guess in range(256):
                forged[position] = guess
                sys.stdout.write(json.dumps({"q": base64.b64encode(bytes(forged) + target).decode()}) + "\n")
                sys.stdout.flush()
                reply = json.loads(sys.stdin.readline())
                if reply.get("pad_ok"):
                    found = guess
                    break
            if found is None:
                raise SystemExit("padding oracle produced no candidate")
            intermediate[position] = found ^ padding
        plaintext.append(bytes(a ^ b for a, b in zip(intermediate, original)))
    value = b"".join(plaintext)
    try:
        value = value[:-value[-1]]
    except (IndexError, ValueError):
        pass
    return {"plaintext_hex": value.hex()}


def main():
    condition, public = instance()
    if condition == "RC4_Keystream":
        claim = {"plaintext_hex": xor_hex(public["c1_hex"], public["c2_hex"]).hex()}
    elif condition == "ChaCha20_Nonce_Repeat":
        claim = {"plaintext2_hex": xor_hex(public["c1_hex"], public["c2_hex"]).hex()}
    elif condition == "ECDSA_Nonce_Reuse":
        claim = ecdsa(public)
    elif condition == "CBC_Padding_Oracle":
        claim = cbc(public)
    else:
        raise SystemExit("unknown condition")
    print("CLAIM:" + json.dumps(claim, separators=(",", ":")))


if __name__ == "__main__":
    main()