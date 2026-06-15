def p(g):A,F,E,*G,H,G=filter(any,g);B=max(A);C=A.index(B);D=E[C+2];return[[(F,(D,B)[F>0])[D in E[-~C::sum(A)//B-3]+G]for(F,*G)in zip(E,F,H)]for E in g]
