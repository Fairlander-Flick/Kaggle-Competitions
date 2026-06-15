p=lambda g,l=4,R=range(21):max(g,key=all)in(A:=[[max(max(A[B%l::l])for A in g[A%l::l])for B in R]for A in R])and A or p(g,-~l)
