import sys
import json

c1_hex = "f3420f30ba760b79dfb6c00586c4ef581737aeb48addf8402fd9c4e84fc1ca413fc6d5124705427c1253c8634f2f162ddb5e46fdf299006e7edc41c9f66662cc"
c2_hex = "a3a08fd9f552040da90670eebd46369d2d6a7d7d5274a89d84c6512bd55a5284884619257e277e367e6797533e52de55580f5420ef1d0c01adb4a0722555bc18"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# c2 is the keystream (since it encrypts all zeros)
# P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))

print(f'CLAIM:{{"plaintext_hex": "{p1.hex()}"}}')
sys.stdout.flush()