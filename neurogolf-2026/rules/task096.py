# (decompressed)
from re import*
def p(i,z=range):
 r=sub(', ','',str(i+[*zip(*i)]));r+=r[::-1];i=int(max(r,key=r.count));l={0:(0,i)}
 for m in z(10):
  if(i^m)*(e:=findall(f'{m}+',r)):n=len((findall(f'{m}{m}([^]){m}]+){m}',r)or[''])[0]);f=len(max(e))*((n>0)+1);l[f+n>>1]=n+1>>1,m
 m=max(l);return[[i*((n:=l[max(abs(x),abs(s))])[0]>min(abs(x),abs(s)))or n[1]for x in z(-m,m+1)]for s in z(-m,m+1)]
