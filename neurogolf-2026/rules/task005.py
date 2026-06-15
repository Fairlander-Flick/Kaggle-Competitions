# (decompressed)
def p(m):
 r=range;f=max(([(i,y)for d in r(9)if m[(i:=t//19+d//3)][(y:=t%19+d%3)]]for t in r(361)),key=len)
 for t in r(45):
  t,n,u=t%3*4-4,t//15*4-4,t%5+1
  for i,y in f:
   if-1<i+n*u<21>y+t*u>-1:m[i+n*u][y+t*u]=max(m[i+n][y+t]for i,y in f)
 return m
