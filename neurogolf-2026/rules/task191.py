# (decompressed)
def p(n):
 y=lambda n:1in n;e=[*zip(*filter(y,zip(*filter(y,n))))];y=enumerate;c=[[0,*n,0]for n in[[0]*23,*n,[0]*23]]
 for r in[0]*4:
  for r in e,e[::-1]:
   for b in range(26-len(r)):
    for t in range(26-len(r[0])):
     if all(c[b+u][t+o]^f<2 for u,n in y(r)for o,f in y(n)):
      for u,n in y(r):
       for o,f in y(n):c[b+u][t+o]|=f
  e=[*zip(*r)]
 return[n[1:-1]for n in c[1:-1]]
