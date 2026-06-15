def p(g):D,A=sorted({*sum(g,[])}-{0},key=lambda c:str(g).count(f"{c}, {c}"));B=[B for B in g if A in B];C=len(B)//3;return[[D*(B==A)for B in E[min(B.index(A)for B in B)::C][:3]]for E in B[::C]]
