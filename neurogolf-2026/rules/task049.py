p=lambda g:[[A]*B.count(A)for B in g if(A:=min({*(C:=sum(g,[]))}-{0},key=C.count))in B]
