p=lambda g:[exec('while-1<i<10>j>-1:g[i][j]=k;i+=a;j+=b')for n in range(256)if(k:=g[i:=n>>5][j:=n>>2&7])*g[i-(a:=(n&2)-1)][j]*g[i+a][j+(b:=n%-2|1)]]and g
