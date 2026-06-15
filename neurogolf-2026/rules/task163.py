def p(g,R=range(11)):C,D=divmod(sum(g,[]).index(4),11);return[[5*(g[A][B]==5)or(A^C%4*4|B^D%4*4<4)*g[C&-4|A&3][D&-4|B&3]for B in R]for A in R]
