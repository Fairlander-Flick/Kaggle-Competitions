# (decompressed)
def p(a):
 f=range
 for d,e,r in[(d,e,3+(a[d][e+3]>0))for d in f(9)for e in f(9)if a[d][e]>a[~-d][e]|a[d][~-e]<1]:
  for u,p in(a[d][e],f(2-r,r*2-2)),(a[d+1][e+1],(0,~-r)):
   for i in f(r):
    for n in p:a[d+n][e+i]=a[d+i][e+n]=u
 return a
