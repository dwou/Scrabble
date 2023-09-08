
with open('TEST.txt','r') as f:
    lines = f.readlines()

for j in range(2,16):
    with open(f'OUT{j}.txt','w+') as f:
        for i in lines:
            if i.index('$') == j: # first index of '$' delimiter
                f.write(i)
