def p(g):
	F=enumerate;B={C|A<<5for(A,B)in F(g)for(C,D)in F(B)if D};G=B|B
	while B:
		H,*C=-1,B.pop()
		for A in C:D={A+1,A-1};E=D|{A+32,A-32};H+=len(G&D)*len(G&E-D);C+=B&E;B-=E
		for A in C:g[A>>5][A&31]=H*5%9+1
	return g
