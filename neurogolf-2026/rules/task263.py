p=lambda g:g[3:]and(A:=sorted((str(A).count('0'),A)for A in zip(*[iter(g)]*3)))[-(A[0]>A[1][:1])][1]or[*zip(*p([*zip(*g)]))]
