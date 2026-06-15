p=lambda g:[g[:(B:=2|len(g)//7)+B][g.index(A)-B][A.index(0):][:C]for A in g if(C:=A.count(0))]
