# (decompressed)
p=lambda h,r=range:(c:=len(h))and[[[max(h[a][m]for a in(a,2*i-a)for m in(e,2*f-e)if-1<a<c>m>-1)for e in r(c)]for a in r(c)]for i in r(1,c-1)for f in r(1,c-1)if 0<h[i][f]==h[i-1][f-1]==h[i-1][f+1]==h[i+1][f-1]==h[i+1][f+1]][-1]
