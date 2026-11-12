import base64

# Decode the artifacts
with open('output.txt', 'r') as f:
    encoded_output = f.read().strip()
    new_flag = base64.b64decode(encoded_output).decode()

# The source code shows the transformation:
# for i in range(0, len(flag), 3):
#     new_flag += flag[i+1]
#     new_flag += flag[i+2]
#     new_flag += flag[i]
# This means each group of 3 characters is rotated: [0,1,2] -> [1,2,0]
# To reverse: if new_flag has [1,2,0], then original flag has [2,0,1]

flag = ''
for i in range(0, len(new_flag), 3):
    # new_flag[i] was originally flag[i+1]
    # new_flag[i+1] was originally flag[i+2]
    # new_flag[i+2] was originally flag[i]
    flag += new_flag[i+2]
    flag += new_flag[i]
    flag += new_flag[i+1]

print(flag)