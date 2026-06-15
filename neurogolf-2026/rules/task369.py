p=lambda g,k=63,m=1:-k*g or p([[((v:=A and A|v,(A<1)*-~(m:=m*2))[k>62],5-A.bit_count())[k<1]for A in(0,)+A][:0:-1]for A in zip(*g)],k-1)
