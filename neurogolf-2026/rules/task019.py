def p(g):
	g=[r*2for r in g*2]
	for a,b in[*zip(g,g[1:]),*zip(g[1:],g)]:b[:]=map(lambda x,y,z:x or(y|z)&7and 8,b,a[1:]+[0],[0]+a)
	return g
