# (decompressed)
def p(e):
 p=8in e[0];e=(e,[*map(list,zip(*e))])[p];f=[z for z,r in enumerate(e)if r[0]]*2
 for z,r in enumerate(e):
  for t,r in enumerate(r):
   for a in f[z>f[1]:(z>f[0])+1][:r&2]:
    for n in e[a:z+1]+e[z:a+1]:n[t]=2
    for n in e[a-1:a+2:2]:n[t-1:t+2]=8,8,8
 return(e,[*zip(*e)])[p]
