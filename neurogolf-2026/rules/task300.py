p=lambda g,k=3:-k*g or[A for A in zip(*p(g,k-1))if max(range(1,10),key=sum(g,[]).count)in A]
