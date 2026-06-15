def p(g,f=filter,z=zip):
	B,A=divmod(sum(g,[]).index(5),len(g[0]));g[B][A]=0
	for(C,D)in z(g[B-1:],z(*f(sum,z(*f(sum,g))))):C[A-1:A+2]=D
	return g
