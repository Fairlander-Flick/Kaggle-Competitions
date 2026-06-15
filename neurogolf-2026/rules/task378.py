def p(a,k=3):C=range(len(a)-2);[exec('a[A+~D][B+~D]=a[A+2][B+2]')for A in C for B in C if(R:=a[A+1])[B+1]<a[A][B]==R[B]==a[A][B+1]for D in C[:A][:B]];return-k*a or p([*map(list,zip(*a[::-1]))],k-1)
