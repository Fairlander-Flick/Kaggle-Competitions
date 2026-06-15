p=lambda g,w=range(4):[[{A.index(0):max(A)for(B,C)in zip(g,g[1:])for A in zip(C[1:],C,B[1:],B)if A.count(0)<2}[A&2|B>>1]*(A*B%3<1)for B in w]for A in w]
