p=lambda g,k=3:-k*g or p([*zip(*[A for A in g[:1]*12+g if A.count(max(max(g,key=any)))^1][:~len(g):-1])],k-1)
