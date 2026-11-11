import base64

with open("encrypted", "rb") as f:
    data = base64.b64decode(f.read().strip())

# The ciphertext is a sequence of length-prefixed records.
# Each record: 1 byte length N, then N bytes of payload.
# Payload format: 1 byte type, 1 byte value, then (N-2) bytes of data.
# Type 0x4c = 'L', 0x41 = 'A', 0x4d = 'M' -> "LAM"
# Type 0x50 = 'P', 0x58 = 'X', 0x50 = 'P', 0x43 = 'C', 0x42 = 'B' -> "PXPCB"
# Type 0x54 = 'T', 0x42 = 'B', 0x4c = 'L' -> "TBL"
# Type 0x4d = 'M', 0x49 = 'I', 0x57 = 'W' -> "MIW"
# Type 0x44 = 'D', 0x46 = 'F', 0x43 = 'C' -> "DFC"

flag = ""
i = 0
while i < len(data):
    n = data[i]
    payload = data[i+1:i+1+n]
    typ = chr(payload[0])
    val = chr(payload[1])
    flag += typ + val
    i += 1 + n

print(flag)
