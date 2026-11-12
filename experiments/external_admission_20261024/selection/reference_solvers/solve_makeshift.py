import sys
# Makeshift: flag reversed, then 3-char blocks have chars 0,1,2 -> 1,2,0
data = open(sys.argv[1]).read().strip()
flag_rev = ""
for i in range(0, len(data), 3):
    blk = data[i:i+3]
    if len(blk) == 3:
        flag_rev += blk[2] + blk[0] + blk[1]
    else:
        flag_rev += blk
print(flag_rev[::-1])
