def p(g,r=224):A,B=r//15,r%15;C=1,0,14;D=sum(g[A-D][B-E]&4for D in C for E in C);g[A][B]-=g[A][B]//8*D and(D<16)+4;r and p(g,r-1);return g
