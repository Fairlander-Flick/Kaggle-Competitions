def p(a):
	A=len(a[0]);F=len(a)*A;G,D=0,3;B=lambda i:i<F and(C:=a[i//A])[j:=i%A]==G and(C.__setitem__(j,D)or-~B(i+A)+B(i+(A>j+1)));E=[(C,A)for A in range(F)if(C:=B(A))];G=D
	for(C,H)in E:D=C==max(E)[0]or(C==min(E)[0])*8;B(H)
	return a
