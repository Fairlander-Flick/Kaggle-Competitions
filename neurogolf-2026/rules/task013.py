p=lambda g:g[0][12:]and[*zip(*p([*zip(*g)]))]or exec('a,b=map(g.index,f:=[*filter(sum,g)]);g[a::b-a]=[[sum(r)]*len(r)for r in f*8][:len(g[a::b-a])]')or g
