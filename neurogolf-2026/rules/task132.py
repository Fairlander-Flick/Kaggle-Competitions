def p(a):
	A=len(a[0]);D=sum(a,[]);E=D.index
	for B in{*D}-{0}:
		C=E(B);F=E(B,C+1);G,H=sorted((C%A,F%A))
		for I in a[C//A:1+F//A]:I[G:-~H]=[B]*(H+1-G)
	return a
