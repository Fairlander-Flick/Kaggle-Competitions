p=lambda g,c=1:(A:=[A for A in zip(*(A for A in g if c in A))if c in A])and len(A)<6>len(A[0])and[*zip(*A)]or p(g,-~c)
