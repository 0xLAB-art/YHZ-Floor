import sys, json

c1_hex = '8156cd513461ea7c2a1690e2c539ef4ff95d07aac7f9164567610d8576bf7f368523077979ef97033c51a2e7113eb4622314bfcc7bf9f3137f616918f8af10c1'
c2_hex = 'ed6e42508a780ac8fb3e850101c66398dfb96504941d6c08f35b8d081655dd71e8302982cca0a16ed8aa773e234c38a99d96ecd30b128eec98ae36677139be04'

b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)

p1_bytes = bytes(a ^ b for a, b in zip(b1, b2))
p1_hex = p1_bytes.hex()

claim = {"plaintext_hex": p1_hex}
print("CLAIM:" + json.dumps(claim))
sys.stdout.flush()