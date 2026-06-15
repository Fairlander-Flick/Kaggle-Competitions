p=lambda g,z=zip:[[A%4*sum(A>=B for A in z(*g))for(A,B)in z(A,z(*g))]for A in g]
