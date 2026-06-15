# (decompressed)
i=range(100)
def p(w):
 a=sum(w,[])
 for d in a:
  n=[w for w in i if a[w]==d]
  r=next((t for t in i if all(a[(x:=w-n[0]+t):x+1]<[1]*all(w+t in n or a[x+t:][:1]==[5]for t in(1,~0,10,~9))for w in n)),~0)
  for w in n*-~r:a[w],a[w-n[0]+r]=0,d
 return[a[w:w+10]for w in i[::10]]
