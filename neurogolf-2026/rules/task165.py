def p(g):
	B=sum(g,[]);*E,C=filter(int,B)
	for A in range(380):
		for D in g[A//20+1:]*(B[A+20]^B[A])*(0<B[A]!=C):D[A%20]=max(B[A+20::20])
	return g
