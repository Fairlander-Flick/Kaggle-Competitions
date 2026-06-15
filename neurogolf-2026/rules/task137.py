def p(g):A=range(len(g));E,(B,C),D=[(B,C)for B in A for C in A if g[B][C]];return[[g[B][C]*(max(D-B,B-D,A-C,C-A)%(B-E[0])<1)for A in A]for D in A]
