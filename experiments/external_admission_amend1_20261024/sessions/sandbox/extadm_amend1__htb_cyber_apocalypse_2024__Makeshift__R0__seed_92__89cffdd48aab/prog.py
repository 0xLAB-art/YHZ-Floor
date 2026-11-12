with open('output.txt', 'r') as f:
    new_flag = f.read().strip()

flag = ''
for i in range(0, len(new_flag), 3):
    flag += new_flag[i+2]
    flag += new_flag[i]
    flag += new_flag[i+1]

original_flag = flag[::-1]
print(original_flag)