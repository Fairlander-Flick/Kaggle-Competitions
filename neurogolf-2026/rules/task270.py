def p(g,i=0,h={}):
	A,B=i//15,i%15;C=g[A][B];h[C]=A,B;i<224and p(g,i+1)
	if C>2:D,E=h[8%C];g[D+(A>D)-(A<D)][E+(B>E)-(B<E)],g[A][B]=C,0
	return g
