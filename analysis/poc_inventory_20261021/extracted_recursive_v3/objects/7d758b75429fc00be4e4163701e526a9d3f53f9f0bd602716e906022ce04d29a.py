import sys
import json
import base64

# Provided ciphertexts
c1_hex = "d0ec99d3b0a89484ba0345a400e766edc73bbc1d4ced286f3988b17deb6a4bb1a15b2593ec4f6ad13fd1f8cc4f0f191f9194120e38b3a913f972c8c9afdcbd64"
c2_hex = "37b16e8cfe806c1e09b97d6cc753aee4a7f58decd7556a1f4e8112a76bfa9cabb8b4daa9def2c28ef1773397804912d6e953870e8c88b467eb7eb9ea33168b6c"

# Convert hex to bytes
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# RC4 keystream reuse attack: ciphertext = plaintext XOR keystream
# c1 = P1 XOR keystream
# c2 = (0x00 * 64) XOR keystream = keystream
# Therefore, P1 = c1 XOR c2
plaintext = bytes([c1[i] ^ c2[i] for i in range(64)])
plaintext_hex = plaintext.hex()

# Output final claim
print(f'CLAIM:{{"plaintext_hex": "{plaintext_hex}"}}')
sys.stdout.flush()