def p(g):
	B,C,D,E,*F=g
	for A in range(16):
		if[5]*4==C[A:A+2]+D[A:A+2]:B[A-1:A+3:3]=1,2;E[A-1:A+3:3]=3,4
	if F:p(g[1:]);return g
