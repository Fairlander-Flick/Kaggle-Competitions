p=lambda g:g+[A.__iadd__(B)[::-1]for(A,*B)in zip(g,*g[::-1])][::-1]
