def p(g):
	B=sum(g,[]);C=sorted(B,key=B.count)
	for A in(0,1,2,3):D,E=divmod(B.index(C[A]),10);g[D+A//2*4-2][E+A%2*4-2],g[D][E]=C[3-A],0
	return g
