# (decompressed)
p=lambda a:(t:=enumerate,n:=sum(a,[]),n:=sorted({*n},key=n.count)[-2:],u:=[(m,e)for m,e in t(a)for e,p in t(e)if{p}-{*n}],f:=[sum({*e}&{*n})%sum(n)for e in a+[*zip(*a)]],s:={f[m]or f[len(a)+e]or n[n[0]in f]:a[m][e]for m,e in u},[[(p,s.get(p,p))[any(e-b in(m-a,a-m)for a,b in u)]for e,p in t(e)]for m,e in t(a)])[ -1]
