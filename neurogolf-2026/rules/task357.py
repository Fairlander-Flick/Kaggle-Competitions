def p(g,t=9):
	for A in g:B=~-len(A);A[:]=[8]*-~B;A[~abs(t%(2*B)-B)]=1;t-=1
	return g
