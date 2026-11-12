with open('output.txt', 'r') as f:
    encrypted = f.read().strip()

flag = ''
for i in range(0, len(encrypted), 3):
    flag += encrypted[i+2]
    flag += encrypted[i]
    flag += encrypted[i+1]

flag = flag[::-1]
print(flag)