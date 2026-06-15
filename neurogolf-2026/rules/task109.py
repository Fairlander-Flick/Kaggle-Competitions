def p(g):A=len(g)>>1;return[B*0!=0and p(B)or(B>0)*g[A]for B in g[:A]+g[A-1::-1]]
