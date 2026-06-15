def p(g):
	for A in(-1,1):
		B,C=divmod(sum(g,[]).index(A%3),10)
		while B<10>C>-1<B:g[B][C]=A%3;B-=A;C-=A
	return g
