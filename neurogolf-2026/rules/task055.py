p=lambda a,m=1602080,h=0:a and[[max(A,m>>(h:=h+A)&7)for A in a.pop(0)]]+p(a,m>>3*(h>16))
