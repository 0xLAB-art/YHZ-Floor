import base64

# Read the encoded output
with open('output.txt', 'r') as f:
    encoded_output = f.read().strip()

# Decode from base64
scrambled = base64.b64decode(encoded_output).decode()

# The source.py shows the flag is processed in chunks of 3:
# for i in range(0, len(flag), 3):
#     new_flag += flag[i+1]  # second char
#     new_flag += flag[i+2]  # third char
#     new_flag += flag[i]    # first char
# So each group of 3 is rotated: ABC -> BCA

# To reverse: if we have BCA, original was ABC
# So from position j in scrambled:
# - scrambled[j] came from position (j//3)*3 + 1
# - scrambled[j+1] came from position (j//3)*3 + 2  
# - scrambled[j+2] came from position (j//3)*3
# Reversing: original[i] = scrambled[i+2], original[i+1] = scrambled[i], original[i+2] = scrambled[i+1]

original = ''
for i in range(0, len(scrambled), 3):
    if i+2 < len(scrambled):
        # Reverse the rotation: BCA -> ABC
        original += scrambled[i+2]
        original += scrambled[i]
        original += scrambled[i+1]
    elif i+1 < len(scrambled):
        # Handle remaining 2 chars
        original += scrambled[i+1]
        original += scrambled[i]
    elif i < len(scrambled):
        # Handle remaining 1 char
        original += scrambled[i]

print(original)
