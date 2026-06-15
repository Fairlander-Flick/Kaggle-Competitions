def p(g,k=3,e=enumerate):D,A,E=zip(*((B,D,A)for(B,C)in e(g)for(D,A)in e(C)if A));B,C=-~min(A),max(A);g[-~D[0]][B:C]=[sum({*E})-5]*(C-B);return-k*g or p([*map(list,zip(*g[::-1]))],k-1)
