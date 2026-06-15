p=lambda g:[exec('while 0<i<9>j>0:g[i:=i+a][j:=j+b]=k')for n in range(256)if(k:=g[(i:=1+n//32)][(j:=1+n//4%8)-(b:=n%-2|1)])*g[i-(a:=(n&2)-1)][j]*g[i-a][j-b]]and g
