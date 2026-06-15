def p(a,r=range):
	*_,C,A,B=min((any(any(A[D:B])for A in a[C:A]),(C-A)*(B-D),a[C:A],D,B)for A in r(-~len(a))for C in r(A-1)for B in r(-~len(a[0]))for D in r(B))
	for D in C:D[A:B]=[6]*(B-A)
	return a
