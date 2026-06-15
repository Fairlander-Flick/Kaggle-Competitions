# (decompressed)
def p(n):
	p=enumerate;r={w+n*1j:a for(n,r)in p(n)for(w,a)in p(r)};t,c=({p for p in r if r[p]&t}for t in(1,2))
	for i in c:t|=c&{p+r for p in t for r in(1,1j,-1,-1j)}
	l,*i=t&c;b=lambda t:{j+(p-l)*i+m%i+m//i*1j for p in t for m in range(i*i)}
	for i in 3,2,1:
		for j in c-t:
			for a in(m:=b(t&c))<=c and b(t-c)&{*r}or():c-=m;n[int(a.imag)][int(a.real)]=1
	return n
