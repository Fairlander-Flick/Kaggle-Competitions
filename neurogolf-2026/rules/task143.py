def p(g):
	i=sum(g,[]);d={}
	for c in i:
		if d.setdefault(sum(q-i.index(c)for q in range(100)if i[q]==c),c)-c:return eval(str(g).replace(str(c),'5'))
