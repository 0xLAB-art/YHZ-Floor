import base64

# Read the encoded output
with open('output.txt', 'r') as f:
    encoded_output = f.read().strip()

# Decode from base64
scrambled = base64.b64decode(encoded_output).decode()

# The source.py shows the scrambling algorithm:
# For every 3 characters at positions i, i+1, i+2
# They are rearranged as: i+1, i+2, i
# To reverse: if new positions are j, j+1, j+2
# They came from positions: j+2, j, j+1 in original

original = ''
for i in range(0, len(scrambled), 3):
    if i + 2 < len(scrambled):
        # scrambled[i] was original[i+2]
        # scrambled[i+1] was original[i]
        # scrambled[i+2] was original[i+1]
        original += scrambled[i+2]
        original += scrambled[i]
        original += scrambled[i+1]
    else:
        # Handle remaining characters if any
        remaining = scrambled[i:]
        if len(remaining) == 1:
            original += remaining[0]
        elif len(remaining) == 2:
            original += remaining[1] + remaining[0]

print(original)