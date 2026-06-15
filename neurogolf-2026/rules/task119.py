def p(g):
	for e in(0,1)*4:
		c,*f=g=(g[::-1],[*map(list,zip(*g))])[e];a=0<(8in c)>sum(c[:(b:=c.index(8))])
		for d in f*a:a-=d[b+a]&2;b+=a;d[b]=d[b]or 3
	return g
