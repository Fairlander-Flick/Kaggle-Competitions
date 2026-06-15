p=lambda g:[A[:4]+(C[:4]+B)[::-1]for(A,*B,C)in zip(g,*g,g[::-1])]
