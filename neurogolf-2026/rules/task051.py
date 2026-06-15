p=lambda g,k=3:-k*g or p([[*r][:(i:=next((i+1for i in range(len(r)-2)if r[i]==0<r[i+1]!=r[i+2]>0),99))]+[x or r[i]for x in r[i:]]for r in zip(*g[::-1])],~-k)
