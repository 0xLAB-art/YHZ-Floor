import json

c1_hex = "d4a4f1d74f508707278f998f07d8f6cb4fdb17eb30d91bf40ed0d1a4b586d9f50260fced624a5cb29884cd3293de521e44d3351ee3133e5edba65885160e293f"
c2_hex = "55f8312c5696b228094552e9b6ab06e5efab88cbaa592a7623bc328a83b1a029b56d8beb9f29b83fbe1d65198f28b0dc8f9c6977f113dd7e718b623868771fde"

a = bytes.fromhex(c1_hex)
b = bytes.fromhex(c2_hex)
p1 = bytes(x ^ y for x, y in zip(a, b)).hex()

claim = {"plaintext2_hex": p1}
print("CLAIM:" + json.dumps(claim))