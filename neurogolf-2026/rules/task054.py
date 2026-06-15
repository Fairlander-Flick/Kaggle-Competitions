# (decompressed)
def p(d):
	u=eval(str(d));g=d[0][0];a=f=range(30);w={(w,j)for w in a for j in a if d[w][j]^g};e=w|w
	while e:
		r=[e.pop()]
		for n,i in r:y=e&{(n+1,i),(n-1,i),(n,i+1),(n,i-1)};r+=y;e-=y
		f=min(f,r,key=len)
	h,v=sorted(f)[len(f)//2]
	for n,i in w:
		for w,j in f*(d[n][i]==d[h][v]):
			for t in a[1:2|28*((w+w-h,j+j-v)in f)]:
				e=u[n+t*(w-h)];r=i+t*(j-v)
				if e[r]==g:break
				e[r]=d[w][j]
			u[w][j]=g
	return u
