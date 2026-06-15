def p(g,k=63):
	B,D,C,*E=g[k>>3:];A=slice(k&7,k%8+3)
	if min(B[A]+C[A]):B[A]=C[A]=0,2,0;D[A]=2,2,2
	if k:p(g,k-1);return g
