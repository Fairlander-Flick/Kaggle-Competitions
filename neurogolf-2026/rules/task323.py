def p(g):
	for C in(-1,1):
		A,B=divmod(sum(g,[]).index(8),13);D=0
		while-1<((B:=B+C)if D&2else(A:=A-C))<13:g[A][B]=5;D+=1
	return g
