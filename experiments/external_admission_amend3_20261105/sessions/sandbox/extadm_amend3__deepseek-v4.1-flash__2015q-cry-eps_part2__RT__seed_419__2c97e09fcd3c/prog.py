import base64

data = open('eps1.9_zer0-day_b7604a922c8feef666a957933751a074.avi', 'rb').read()
raw = base64.b64decode(data)
flag = raw.decode('ascii')
print(flag)