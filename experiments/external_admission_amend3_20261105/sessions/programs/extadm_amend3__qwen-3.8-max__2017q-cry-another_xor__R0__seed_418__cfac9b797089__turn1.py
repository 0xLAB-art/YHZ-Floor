import sys

with open('encrypted', 'rb') as f:
    data = f.read().strip()

if data.startswith(b'274c10121a0100495b502d551c557f0b0833585d1b27030b5228040d3753490a1c025415051525455118001911534a0052560a14594f0b1e490a010c4514411e070014615a181b02521b580305170002074b0a1a4c414d1f1d171d00151b1d0f480e491e0249010c150050115c505850434203421354424c1150430b5e094d144957080d4444254643'):
    data = bytes.fromhex(data.decode().strip())

key = b'CTF{'}
result = bytearray()
for i, b in enumerate(data):
    result.append(b ^ key[i % len(key)])

print(result.decode('latin-1'))