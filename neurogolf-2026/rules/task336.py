def p(a,T=range(10)):
	(C,D),*G,(E,F)=[(A,B)for A in T for B in T if a[A][B]]
	for A in T[C:E+1]:
		for B in T[D:F+1]:
			while~A*~B%11>0==a[A][B]:a[A][B]=8;A+=(A>C)-(A<E);B+=(B>D)-(B<F)
	return a
