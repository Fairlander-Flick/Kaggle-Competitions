p=lambda g,k=15,m=1:-k*g or p([[((B:=A and(A|B,m:=m*2)[k>14]),-A.bit_count()%5)[k<1]for A in(0,)+A][:0:-1]for A in zip(*g)],k-1)
