def p(j):A=len(j[:len(j[0])]);B=range(A*A);return[[sum(j[C%A+B-A][D%A+B-A]//8*j[C//A-B][D//A-B]for B in(0,A))for D in B]for C in B]
