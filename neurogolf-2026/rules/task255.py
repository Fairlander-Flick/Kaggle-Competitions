# (decompressed)
def p(e):
	m=n=h=l=a=b=0;x,f,u,y,g,=30,15,29,all,range
	d,i=lambda f:[[f[j][u-r]for j in g(x)]for r in g(x)],lambda f:[[f[u-j][r]for j in g(x)]for r in g(x)]
	for r in g(x):
		for j in g(16):m+=y(e[r][j+f]<1for f in g(f));n+=y(e[j+c][r]<1for c in g(f))
	if m<n:e=i(e)
	for c in g(2):
		a=l=y(e[0][j]<1for j in g(f))
		for r in g(1,x):
			if y(e[r][j]<1for j in g(f)):l+=1
			else:a=max(a,l);l=0
		if h<a:h=a;b=c
		e=i(i(e))
	if b:e=i(i(e))
	for j in g(x):
		for r in g(x-h+1):
			if y(e[r+c][f]<1for c in g(h)for f in g(j+1)):a=r;l=j+1
	if l<x:l-=1
	for r in g(1,h-1):
		for j in g(l):e[a+r][j]=3
	e=i(e)
	for c,h in((0,x-a-h+1),(u-a,x)):
		if y(e[f][j]<1for j in g(c,h)for f in g(2)):
			for j in g(c,h):e[0][j]=3
		if y(e[x-2+f][j]<1for j in g(c,h)for f in g(2)):
			for j in g(c,h):e[u][j]=3
		for r in g(1,l-1):
			if y(e[r+f][j]in[0,3]for j in g(c,h)for f in g(-1,2)):
				for j in g(c,h):e[r][j]=3
	if b:e=i(i(e))
	if m<n:e=d(e)
	return d(e)
