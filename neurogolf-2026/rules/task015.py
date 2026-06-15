p=lambda g:([exec('x,y=1,A-1;'+'g[i//9+x][i%9+y]=A^6;x,y=-y,x;'*4)for i in range(81)if 3>(A:=g[i//9][i%9])>0],g)[1]
