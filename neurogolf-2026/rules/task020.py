def p(g,E=enumerate):
	P=[(r,c,v)for(r,R)in E(g)for(c,v)in E(R)if v];a,b,_=map(min,zip(*P))
	for(r,c,v)in P:exec('r,c=a+b+4-c,b-a+r;g[r][c]=v;'*3)
	return g
