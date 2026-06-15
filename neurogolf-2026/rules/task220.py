p=lambda g,e=enumerate:[[(sum(sum((0,*A)[B:B+3])for A in[[],*g][A:A+3])+C)*5%9for(B,C)in e(B)]for(A,B)in e(g)]
