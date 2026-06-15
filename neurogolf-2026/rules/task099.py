def p(g):
	for A in(0,1,4):
		for(B,C)in zip(g,g[1:]):B[A:A+5]=[B or max([*zip(*g)][A+2])*C[A]*C[A+4]for B in B[A:A+5]]
	return g
