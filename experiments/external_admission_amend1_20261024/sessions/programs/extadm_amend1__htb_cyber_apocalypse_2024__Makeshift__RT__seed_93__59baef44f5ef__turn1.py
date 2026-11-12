import base64

# Decode the output
with open('output.txt', 'r') as f:
    encoded_output = f.read().strip()
    new_flag = base64.b64decode(encoded_output).decode()

# The source.py shows the transformation:
# for i in range(0, len(flag), 3):
#     new_flag += flag[i+1]
#     new_flag += flag[i+2]
#     new_flag += flag[i]
# 
# This means every 3 characters are rotated: [0,1,2] -> [1,2,0]
# To reverse: [1,2,0] -> [0,1,2], so new position mapping:
# new_flag[0] (was flag[1]) -> flag[1]
# new_flag[1] (was flag[2]) -> flag[2]
# new_flag[2] (was flag[0]) -> flag[0]
# So: flag[0] = new_flag[2], flag[1] = new_flag[0], flag[2] = new_flag[1]

flag = ''
for i in range(0, len(new_flag), 3):
    flag += new_flag[i+2]
    flag += new_flag[i]
    flag += new_flag[i+1]

print(flag)