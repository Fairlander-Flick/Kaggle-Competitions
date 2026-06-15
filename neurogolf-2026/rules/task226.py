def p(g):
	def A(x,y):
		if-1<x<10>y>=g[x][y]<1:g[x][y]=B;A(x-1,y),A(x+1,y),A(x,y-1),A(x,y+1)
	B=2;A(4|g[4][0],4|g[0][4]);B=1;A(0,0);B=3;A(9,9);return g
