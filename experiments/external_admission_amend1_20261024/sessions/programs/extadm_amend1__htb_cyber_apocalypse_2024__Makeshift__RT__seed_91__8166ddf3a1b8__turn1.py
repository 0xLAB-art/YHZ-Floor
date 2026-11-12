import base64

# Decode the output
with open('output.txt', 'r') as f:
    encoded_output = f.read().strip()
    new_flag = base64.b64decode(encoded_output).decode()

# The encoding process takes characters in groups of 3:
# original[i], original[i+1], original[i+2]
# and rearranges them to:
# original[i+1], original[i+2], original[i]
# So to reverse: if new_flag has characters at positions j, j+1, j+2
# they came from original[i+1], original[i+2], original[i]
# which means: new[j]=orig[i+1], new[j+1]=orig[i+2], new[j+2]=orig[i]
# To reverse: orig[i]=new[j+2], orig[i+1]=new[j], orig[i+2]=new[j+1]

flag = ''
for i in range(0, len(new_flag), 3):
    flag += new_flag[i+2]
    flag += new_flag[i]
    flag += new_flag[i+1]

# The original code used FLAG[:-1], so we need to add back the last character
# Looking at the pattern, the last character would have been '}'
flag += '}'

print(flag)