import base64

# Read the encoded output
with open('output.txt', 'r') as f:
    encoded_output = f.read().strip()

# Decode from base64
new_flag = base64.b64decode(encoded_output).decode()

# The source.py shows the encoding process:
# flag = FLAG[:-1]  # removes last character
# for i in range(0, len(flag), 3):
#     new_flag += flag[i+1]
#     new_flag += flag[i+2]
#     new_flag += flag[i]
# This swaps each triplet from [i, i+1, i+2] to [i+1, i+2, i]

# To reverse: each triplet [a, b, c] in new_flag came from [c, a, b] in original
# So we need to rearrange: position 0->2, position 1->0, position 2->1
flag = ''
for i in range(0, len(new_flag), 3):
    flag += new_flag[i+2]
    flag += new_flag[i]
    flag += new_flag[i+1]

print(flag)