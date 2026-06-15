# (decompressed)
def p(b,g=2,v={}):
 n=range(9)
 for y in range(len(b)-2):
  for x in range(len(b[0])-2):
   u=bytes(b[y+i//3][x+i%3]==g&2 for i in n)
   if g&2 and(r:=sum(l:={b[y+i//3][x+i%3]for i in n})-2)and l=={2,r}:
    t=[u,r]
    for _ in 0,0,0,0:v[u]=t;u=u[2::3]+u[1::3]+u[::3]
    for i in n:b[y+i//3][x+i%3]=0
   if g<2 and(t:=v.get(u))and(u in t)**g:
    r=t[1];t*=0
    for i in n:b[y+i//3][x+i%3]=2*u[i]or r
 return g and p([*map(list,zip(*filter(any,zip(*filter(any,b)))))],g-1)or b
