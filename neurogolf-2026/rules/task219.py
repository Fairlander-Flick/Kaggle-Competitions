# (decompressed)
def p(o):
 f=enumerate;p=[];m=-2
 for r,n in f(o):
  if any(n):p+=[set()]*(r-1>m);p[-1]|={(r,n)for n,a in f(n)if a};m=r
 g,*e=p
 for e in e:
  for r,n in max((len((d:={(r-min(g)[0]+min(e)[0]-(2<s),n+(s<3)*s)for r,n in g})&e),s,d)for s in range(-2,4))[2]:
   try:o[r][n]|=n>max(n for r,n in e)
   except:0
 return o
