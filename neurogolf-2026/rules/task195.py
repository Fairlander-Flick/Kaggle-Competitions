def p(I,f=filter,r=range(9)):*A,=f(any,zip(*f(any,I)));return[[A[C][B]&A[C*3%9][B*3%9]for C in r]for B in r]
