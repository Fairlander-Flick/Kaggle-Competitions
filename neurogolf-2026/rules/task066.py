# (decompressed)
def p(z):
 b=len(z);s=sum(z,[]);l=lambda m:[*map(list,zip(*m))];r=lambda*m:range(min(m),-~max(m));(i,f),(u,e)=n=[divmod(s.index(m),b)for m in(2,3)]
 if z[i][f+1]^2:return l(p(l(z)))
 m=min(m for m in range(b)if min(8^z[i][f]for i,g in n for f in r(g,m))*(8 in z[u][m-1:m+2])*(z[i+(u<i)*2-1][m]>3)*(sum(z[i][m]for i in r(i,u))<1))
 for i,g in n+[(i,m)for i in r(i,u)]:
  for f in r(g,m):z[i][f]=z[i][f]or 3
 return z
