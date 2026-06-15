def p(g):
	for _ in' '*4:
		for(a,c)in enumerate((g:=[*zip(*g[::-1])])):
			for g[a]in({*c}=={0,2})*[*filter(sum,g[-~a:])]:a-=1
	return eval(f"{g}".replace(*'03'))
