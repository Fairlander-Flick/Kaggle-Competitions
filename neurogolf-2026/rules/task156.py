def p(a):
	C=E=0;D,A,*G=a
	for F in G:
		C|=A<D
		for B in range(9):
			if A[B-1]*A[B+1]*D[B]*F[B]:A[B]=C+1;E+=1|-C
		D,A=A,F
	return[[A^3*(E>0<A<3)for A in A]for A in a]
