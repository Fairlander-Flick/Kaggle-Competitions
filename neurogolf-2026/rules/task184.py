from itertools import*
p=lambda g,h=lambda g:zip(*[map(max,*b)for(k,b)in groupby(g,any)if k]):[*h(h(g))]
