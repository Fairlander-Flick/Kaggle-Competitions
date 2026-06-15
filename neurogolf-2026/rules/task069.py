def p(a):
	C=range(100);A=sum(a,[]);a=A*1;D=[B for B in C if A[B]&7]
	for E in C:
		for B in D*(a[E]==8):a[B],a[E+B-D[0]]=0,A[B]
	return[*zip(*[iter(a)]*10)]
