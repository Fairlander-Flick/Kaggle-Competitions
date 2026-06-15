p=lambda g:exec('for r in g:r[r[0]in r[1:]]|=r[0]\ng[:]=map(list,zip(*g[::-1]))\n'*4+'for r in g[2:-2]:r[2:-2]=[0]*(len(r)-4)')or g
