p=lambda g,k=2:[[max(sum(g,[])[(k:=-~k)%3::3])for _ in r]for r in g]
