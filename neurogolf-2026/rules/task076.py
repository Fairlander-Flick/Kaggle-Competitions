# (decompressed)
def p(g):
 e=enumerate;a={h+1j*i:y for h,i in e(g)for i,y in e(i)if y};e=[min(a,key=a.get)];d=0
 for y in e:e+=[n for n in a if(abs(n-y)<2)>(n in e)];d+=y*(a[y]==2)
 for h in a:
  for n in range(8):
   for i,y in(j:=[(a[y],h+(y-d-(n>>2)*2j*(y-d).imag)*1j**n)for y in e])*all(a.get(i,h|1)==h for h,i in j):g[int(y.real)][int(y.imag)]=i
 return g
