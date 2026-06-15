# (decompressed)
def p(e,s=enumerate):
 m=v={(m,n)for m,v in s(e)for n,r in s(v)if r==2}
 for x in m:m={(v,r)for v,n in m for r,f in m if-3<r-v<3>f-n>-3 for v in range(min(v,r),-~max(v,r))for r in range(min(n,f),-~max(n,f))}
 for n,r in m-v:e[n][r]=4
 return e
