def p(I):
	h=len(I);g=eval(str(I));r=range
	for k in r(h*h):
		y,x=k//h,k%h;k=[*I[y],0].index(0,x);t=k-x>>1
		for j in r(y-t,h):
			for i in r(x-t,k+t):
				if j>-1<i<h:g[j][i]|=I[j][i]or(3,k>i>=x)[j>y+t]
	return g
