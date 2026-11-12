import sys

c1_hex = "d1d4378170381b477eb824bebf1739c694fa759354691df563ff1464cbdf52ae0665481bb06ed98bd0d6561a5c24aacfb45b69d56add9c9881360b21d4139a1f"
c2_hex = "abde796d53d6c5f21fac1a01a4c54af04d84505b7cfd9f9b08175215fcd230e1b579dd8ea1279ebbdbcc9957d68e02c6347d070a26ec985117c4b1959acbdc06"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1 = bytes(a ^ b for a, b in zip(c1, c2))

claim = {"plaintext_hex": p1.hex()}
print(f"CLAIM:{claim}", flush=True)