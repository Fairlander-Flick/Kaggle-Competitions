def p(a):
	B=sum(a,[]).index;A=len(a[0])
	for C in(0,1,-1,A,-A):C+=B(1)+B(1,-~B(1))>>1;a[C//A][C%A]=3
	return a
