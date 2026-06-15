# (decompressed)
def p(c,p=enumerate):(o,i),*m,(n,d)=[(e,f)for e,r in p(c)for f,m in p(r)if m==4];u=[(f,m,e)for e,r in p(c)for f,m in p(r)if m*(e-o|n-e|f-i|d-f<0)];m,a,e=u[0];return[f%(n-o)and[r[i],*c[e+~-f][min(u)[0]:][:d+~i][::a==r[i]or-1],r[d]]or r[i:-~d]for f,r in p(c[o:-~n])]
