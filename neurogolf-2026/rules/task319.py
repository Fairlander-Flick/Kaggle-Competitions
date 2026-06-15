# (decompressed)
def p(g):f=sum(g,[]);m=max;t=f.count;z=m(f,key=t);d={v:[divmod(n,len(g[0]))for n,e in enumerate(f)if e==v]for v in{*f}-{z}};a=m(d,key=t);f=m(d,key=lambda u:(m(map((b:=[(t-2*m-n%2,z-2*i-(n>1))for t,z in d[a]for m,i in d[u]for n in range(4)]).count,b))-2*t(u),t(u)));o,e=zip(*d[f]);return[[[z,v][v==f]for v in v[min(e):-~m(e)]]for v in g[min(o):-~m(o)]]
