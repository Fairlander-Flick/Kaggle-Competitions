# (decompressed)
def p(w):
	s=range(13)
	for n in 3,2:
		b={(u,i)for u in s for i in s if w[u][i]==n}
		for k in b:
			l=[k]
			for e,f in l:l+=[(u,i)for r in range(9)if(u:=e+r//3-1)in s and(i:=f+r%3-1)in s and w[u][i]and(u,i)not in l]
			if l[1:]:
				for e,f in b-{k}:
					for u,i in l:w[u+e-k[0]][f+(i-k[1])*(2*n-5)]=w[u][i]
				break
	return w
