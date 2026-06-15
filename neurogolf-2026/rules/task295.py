def p(g):A,=g;return g+[(A:=A[:1]+A[:-1])for B in A[3::2]]
