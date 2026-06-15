def p(g):
	A=sum(g,[]);B=[(B//9,B%9)for B in range(81)if A[B]];G,H=B[0]
	for(E,F)in B:
		for(C,D)in B*(A[E*9+F]==2):
			while-1<C<9>D>-1:g[C][D]=sum({*A})-2;C-=G-E|1;D-=H-F|1
	return g
