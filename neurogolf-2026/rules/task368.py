def p(j,B=range(100)):
	A=sum(j,[]);C=[B for B in B if A[B]%5]
	for D in B:
		for E in C*(A[D]==5):A[D+E-C[0]]=A[E]
	return[A[B:B+10]for B in B[::10]]
