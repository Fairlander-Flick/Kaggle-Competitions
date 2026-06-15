p=lambda g:exec('C=A=0;B=len(g);E,D=-1,1\nwhile B>0:exec("g[C:=C+A][E:=E+D]=3;"*B);D,A=-A,D;B-=C<1or 2*A*A')or g
