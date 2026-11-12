import json
import base64

c1_hex = "e5d03f89bc14709cc2a80f2a562371cf04edd7000a2219e7888574079ffbc19f777f7f61a380324378240ec12cee6f3768b1a37a005b555418c40d1a5f86d2a0"
c2_hex = "209945a7f033370557d3c3e30db37e808512085d61abe06b96b2c282bfc7abf2713aa0d0574b0eecd324c1894a40ca690d708edd1fc335fa2259478d9358a144"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# RC4 keystream reuse: c1 = P1 XOR keystream, c2 = zeros XOR keystream = keystream
# Therefore, P1 = c1 XOR c2
plaintext = bytes([c1[i] ^ c2[i] for i in range(len(c1))])
plaintext_hex = plaintext.hex()

print(f"CLAIM:{json.dumps({'plaintext_hex': plaintext_hex})}")