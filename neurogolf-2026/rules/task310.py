p=lambda g,a=0:a and[A for A in zip(*g)if min(a,key=a.count)in A]or p(p(g,(a:=sum(g,[]))),a)
