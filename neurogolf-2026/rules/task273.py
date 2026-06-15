def p(g):
	A=B=0
	for C in g:
		try:D=C.index;A=D(4)+1;B^=D(4,A)-A
		except:C[A:A+B]=[2]*B
	return g
