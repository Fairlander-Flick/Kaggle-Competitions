def p(g):
	for A in(0,1)*4:
		B,*C=g=(g[::-1],[*map(list,zip(*g))])[A];A=0
		for D in C*(('[2'in str(g))-('8'in str(C))):A+=D[0]>1;D[A:]=B[:-A]or B
	return g
