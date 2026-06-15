p=lambda i,R=range:next(i for e in[3,2]for a in R(8)for b in R(8)if min(min(r[b:b+e])for r in i[a:a+e])and[exec(f"n,x={a+b+e-1}-x,{b-a}+n;i[n][x]=c;"*3)for n in R(10)for x in R(10)if(c:=i[n][x])])
