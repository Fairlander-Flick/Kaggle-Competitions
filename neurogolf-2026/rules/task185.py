def p(g):
	A={*g[0]};B=zip
	for C in A:g=[B for B in B(*g)if{*B}-A]
	return[[B*(B==C==D==E!=sum(A))for(B,C,D,E)in B(C,C[1:],D,D[1:])]for(C,D)in B(g,g[1:])]
