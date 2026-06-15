p=lambda g,k=9:(A:=[*filter((B:={k}.issubset),zip(*filter(B,g)))])and{*A[0]}=={k}and[*zip(*A[1:~0])][1:~0]or p(g,~-k)
