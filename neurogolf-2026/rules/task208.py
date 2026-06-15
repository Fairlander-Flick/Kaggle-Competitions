# (decompressed)
def p(a):
	o=sum(a,[]);c=o.count;k=min(o,key=c);u=~-sum(k in r for r in a);i=c(k)//2-u
	for s in range(21-u):
		for e in range(21-i):sum(sum(r[e+1:e+i])for r in a[s+1:s+u])or exec('for r in a[s:s-~u]:r[e]=r[e+i]=k;a[s][e:e-~i]=a[s+u][e:e-~i]=[k]*-~i')
	return a
