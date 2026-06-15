def p(a):s=sum(a,[]);c=s.count;a=sorted({*s},key=c)[::-1];return[[v*(i<c(v))for v in a]for i in range(c(a[0]))]
