import json
c1 = bytes.fromhex('0814c4aae0f4fa27b4622838234f02da0cf19d76baf2fb265a2338b9fd0556ba69fe0b66b944a9da0fadb59f05e09e98edefdd84e848176794b9030cdb7e936a')
c2 = bytes.fromhex('d4212ae141f5135cbdaeb66fceb424868d7d93773f78e05de6f94a924d49ca283a9c36c88ea5ae25029013851edd92f0cea1111f4f23154f7de2f8d60a6078cf')
p1 = bytes(a ^ b for a, b in zip(c1, c2))
print('CLAIM:' + json.dumps({'plaintext2_hex': p1.hex()}))