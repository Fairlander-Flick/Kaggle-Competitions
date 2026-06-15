def p(g):A=g.count(g[0]);B=max(g);C=[g[9][A:]+[0]*A]*10;C[A+g.index(B)]=B;return C
