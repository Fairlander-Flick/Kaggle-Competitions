def p(a,k=3):
	for(A,D)in enumerate(zip(*a)):
		C=-~bytes(D).find(b'\x00\x02');B=(*D[C:],0).index(0)
		for E in a[:C]:E[A-B+1:A+B]=a[C][A-B+1:A+B]
	return-k*a or p([*map(list,zip(*a[::-1]))],k-1)
