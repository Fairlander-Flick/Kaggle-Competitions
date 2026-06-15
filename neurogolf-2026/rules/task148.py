def p(g):
	A=g[4][0]-1
	for B,D in zip(*[[A for A in g if A[B]]for B in(0,-1)][::A]):
		if 8in B:C=B[::A];E=C.index(8);C[1:-~E]=[8]*~-E+[4];B[::A]=C;D[::A]=[8]*~-len(D)+[2]
	return g
