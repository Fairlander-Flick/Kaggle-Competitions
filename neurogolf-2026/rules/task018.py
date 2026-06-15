# (decompressed)
def p(u):
	e=len;n,r=e(u),e(u[0]);g=set();s=lambda i,o:n>i>-1<o<r and(e:=u[i][o])and(exec('u[i][o]=0')or[(e,i,o)]+s(i+1,o)+s(i-1,o)+s(i,o+1)+s(i,o-1))or[]
	for f in[t for d in range(n*r)if 3<e((t:=s(d//r,d%r)))or g.update(t)]:
		i,a,s=f[0]
		for d in range(n*r*4):
			if e((t:={(l,(o-s,s-o,o-s,a-i)[d&3]+d//4//r,(i-a,i-a,a-i,o-s)[d&3]+d//4%r)for l,i,o in f})&g)>2:
				for t,i,o in t:u[i][o]=t
	return u
