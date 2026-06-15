p=lambda g:exec('g[:]=map(list,zip(*g[::-1]))\nfor r in g:\n for i in range(1,bytes(r).find(3)):r[i]|=r[i-1]\n'*4)or g
