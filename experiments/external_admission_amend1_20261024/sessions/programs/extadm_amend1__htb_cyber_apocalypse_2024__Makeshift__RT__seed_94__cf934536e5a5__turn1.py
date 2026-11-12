import base64

# Decode the output
with open('output.txt', 'r') as f:
    encoded_output = f.read().strip()
    new_flag = base64.b64decode(encoded_output).decode()

# The source.py takes the flag (without last char) and rearranges every 3 chars
# from [i, i+1, i+2] to [i+1, i+2, i]
# To reverse: if new_flag has chars at positions [j, j+1, j+2],
# they came from original positions [i+2, i, i+1] where i = j
# So to get original: [j+1, j+2, j] -> [j, j+1, j+2]

original = []
for i in range(0, len(new_flag), 3):
    if i + 2 < len(new_flag):
        # new_flag[i] was at original[i+2]
        # new_flag[i+1] was at original[i]
        # new_flag[i+2] was at original[i+1]
        original.append(new_flag[i+1])
        original.append(new_flag[i+2])
        original.append(new_flag[i])
    elif i + 1 < len(new_flag):
        original.append(new_flag[i+1])
        original.append(new_flag[i])
    else:
        original.append(new_flag[i])

flag = ''.join(original) + '}'
print(flag)