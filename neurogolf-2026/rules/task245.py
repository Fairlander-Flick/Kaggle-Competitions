def p(g):
	A=len(g[0]);B=sum(g,[]);C=[(B//A,B%A)for(B,C)in enumerate(B)if C%3];G,H=map(min,*C);D=~B.index(3)
	for(E,F)in C:g[E][F]^=2;g[E-G-D//A][F-H-D%A]^=2
	return g
