p=lambda g:g[3:]and(A:=g[:len(g)>>1])*2==g and A or[*zip(*p([*zip(*g)]))]
