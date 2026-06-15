def p(g,R=range(19)):
	for B in R:
		for A in R:C,D=g[B],g[~B];C[A]|=C[~A]|D[A]|D[~A]
		for A in R[B+2:~B:2]:g[A][B]=C[A]=C[B+2]
	return g
