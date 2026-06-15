p=lambda g,r=range,l=len:max((l(str(B)),[[max({*A,*B}-{A[0]}or A)for B in zip(*B)]for A in B])for C in r(l(g))for A in r(l(g[0]))for D in r(C*A)if l({*str((B:=[B[D%A:A]for B in g[D//A:C]]))})<7)[1]
