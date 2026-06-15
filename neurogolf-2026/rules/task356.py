p=lambda g,e=enumerate,m=max:[[m(B[:C+1])&m(B[C:])|m(D[:A+1])&m(D[A:])for(C,D)in e(zip(*g))]for(A,B)in e(g)]
