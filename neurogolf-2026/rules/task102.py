def p(g,d=1536):
	while d:
		d-=1;A,B=d&7,d>>7;C=A+2;D=g[d>>3&15:][:C];E=[C*[5]]
		for F in([A[B:B+C]for A in D]==E+A*[[5,*[0]*A,5]]+E)*D[1:-1]:F[B+1:B-~A]=A*[2]
	return g
