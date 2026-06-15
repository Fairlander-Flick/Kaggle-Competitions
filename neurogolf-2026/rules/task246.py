def p(g):
	D=sum(g,[]).index;A=len(g[0]);B,C=D(2),D(3)
	while(B:=B+((C%A>B%A)-(C%A<B%A)or(A,-A)[B>C]))^C:g[B//A][B%A]=8
	return g
