# (decompressed)
def p(u,a=len):
	g=a(u)
	def w(p,n):
		if-1<p<g>n>-1<1>u[p][n]:o[p,n]=r[p]=f[n]=u[p][n]=4;w(p+1,n);w(p-1,n);w(p,n+1);w(p,n-1)
	for e in range(g*g):
		o,r,f={},{},{};w(e//g,e%g)
		for p,n in o:u[p][n]-=a(o)==a(r)*a(f)>1
	return u
