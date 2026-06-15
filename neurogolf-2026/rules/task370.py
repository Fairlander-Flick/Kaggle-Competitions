def p(a):
	A=sum(a,[]);B=len(a[0]);G=sum({*A})-A[0];I,C=divmod(A.index(G),B);H=[(A//B,A%B)for(A,C)in enumerate(A)if 1>C];L,J,K=max((D*D,D,C-A)for(B,A)in H if(D:=I-B)in(C-A,A-C))
	for(E,F)in H:
		while len(a)>(E:=E+J)>-1<(F:=F+K)<B:a[E][F]=G
	return a
