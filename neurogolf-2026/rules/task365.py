p=lambda i,t=zip:i[(A:=(*map(any,i),0).index(0)):]and max(p(i[:A]),p(i[A+1:]),key=lambda z:str(z).count('2'))or t and[*t(*p([*t(*i)],0))]or i
