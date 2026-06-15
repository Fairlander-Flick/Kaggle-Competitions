def p(g,k=323):
	k and p(g,k-1);A=g[k//18:][:3];k%=18
	for B in A*all(1>max(A[k:k+3])for A in A):B[k:k+3]=1,1,1
	return g
