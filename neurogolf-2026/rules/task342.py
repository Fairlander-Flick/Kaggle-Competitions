def p(g):
	C=sum(g,[]);A=C.index(8);g=[10*[0]for A in g];B=0
	for D in C:g[A//10+(B>A)][A%10+(B%10>A%10)]|=D*(D!=8);B+=1
	return g
