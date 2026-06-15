# (decompressed)
def p(o,y=enumerate):
 (e,z),*a,(c,a)=[(c,x)for c,n in y(o)for x,a in y(n)if a&4]
 g=[(a,t,u)for t,n in y(o[c+1:])for a,u in y(n)if u]
 o=[n[z:a+1]for n in o[e:c+1]]
 a=[(d,c-t*d-n//d,x-a*d-n%d)for d in(2,3,4)for c,n in y(o)for x,k in y(n)if k for a,t,u in g if k==u for n in range(d*d)]
 d,c,x=max(a,key=a.count)
 for a,t,u in g:
  for n in range(d*d):o[c+t*d+n//d][x+a*d+n%d]=u
 return o
