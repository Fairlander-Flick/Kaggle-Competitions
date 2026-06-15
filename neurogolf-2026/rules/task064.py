p=lambda g:exec('*_,d,e=sorted(range(10),key=sum(g,[]).count)\n'+'for a in g:\n for b in range(1,bytes(a).find(d)):a[b]=a[b-(a[b]==e)]\ng[:]=map(list,zip(*g[::-1]))\n'*4)or g
