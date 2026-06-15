def p(g):
	for B in(C:=sum(g,[])):
		A=C.index(B)
		while C[(A:=A+11-2*(B in C[A+9::9]))]<B:g[A//10][A%10]=B
	return g
