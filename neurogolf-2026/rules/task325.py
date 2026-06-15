def p(g):C=enumerate;A={D+A*1j:E for(A,B)in C(g)for(D,E)in C(B)};B=lambda z:A.pop(z,0)and B(z+1)|B(z-1)|B(z+1j)|B(z-1j)|1;A=sum(map(B,A|A));return[[0]*B+[8]+[0]*(A+~B)for B in range(A)]
