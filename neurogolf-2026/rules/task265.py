p=lambda g,k=18:g*(k<2)or(G:=eval(str(g)),[exec('r[j:j+2]=2,2')for i in range(19-k)for j in range(17)if 1>max(t[j]|t[j+1]for t in G[i:i+k])for r in g[i:i+k]],p(g,k-1))[2]
