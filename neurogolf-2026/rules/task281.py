p=lambda g:exec('try:*_,b,d=[i for i,r in enumerate(g)if any(r)];D=d-b;1/(D>1);g[b:d+1]=[g[b-1]]*D+[g[b]]\nexcept:0\ng[:]=map(list,zip(*g[::-1]))\n'*4)or g
