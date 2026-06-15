# (decompressed)
def p(l):
	p,h=range,eval(str(l));d=p(len(l)-1)
	def f(a,r,x):
		try:1/(h[a][r]==n[x]>0);h[a][r]=0;[(s>>2 or l[(a,z-~z-a)[s>1]].__setitem__((r,t-~t-r)[s&1],n[x^s]),f(a+s//3-1,r+s%3-1,x))for s in p(9)]
		except:0
	for z in d:
		for t in d:3<len({*(n:=h[z][t:t+2]+h[z+1][t:t+2])})and[f(z+i//2,t+i%2,i)for i in p(4)]
	return l
