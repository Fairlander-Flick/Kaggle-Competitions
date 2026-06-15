def p(j):C=max(j);B=sum(C)//2;A=D=j.index(C)+B;exec('j[D-A][:A]=[2+(A>B)-(A<B)]*A;A-=1;'*D);return j
