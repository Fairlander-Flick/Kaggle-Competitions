def p(g,b=80):
	B,A=b//9,b%9;C=g[B][A:A+2]+g[B+1][A:A+2]
	for D in g[B+2:][:len({*C})*all(C)]:D[A:A+2]=3,3
	if b:p(g,b-1);return g
