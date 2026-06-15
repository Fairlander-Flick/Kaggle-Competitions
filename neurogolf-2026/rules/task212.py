def p(g,a=99):
	A=a//10;C=g.index(max(g));B=g[A][a%10]
	for D in g[A:(A,None,C)[B%3]:B&1^(A<C)or-1]:D[a%10]=B
	if a:p(g,a-1);return g
