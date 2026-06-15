p=lambda g:g and[sum(zip(*[g[1][1::2]]*4),())]*4+p(g[2:])
