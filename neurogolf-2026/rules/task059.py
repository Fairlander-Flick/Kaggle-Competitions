def p(g,r=range(11)):
	A=[0]*11
	for B in r:
		for C in r:
			if(D:=g[B][C])%5:A[B&12|C>>2]+=1;E=D
	return[[[5,E*(A[B&12|C>>2]==max(A))][B&3<3>C&3]for C in r]for B in r]
