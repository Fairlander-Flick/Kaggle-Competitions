def p(i):
	c=sum(i,[]);d,e={},0
	for g in c:
		f=b=();h=[e]
		for a in h:
			if c[a]%5:c[a]=0;f+=a,;b+=a-e,;h+=a-1,a+1,a+20
		d[b]=d.get(b,f)+f;e+=1
		if g&2:j,k=g,b
	for x in d[k]:i[x//20][x%20]=j
	return i
