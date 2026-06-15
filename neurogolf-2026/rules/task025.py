p=lambda g:any(B:=(*map(min,*g),0))*[[B[A+(0<B[A+1]in C[:A])-(0<B[A-1]in C[A:])]for A in range(len(C))]for C in g]or[*zip(*p([*zip(*g)]))]
