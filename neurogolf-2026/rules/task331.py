p=lambda g:[(g:=[*zip(*eval(str(g).replace('1, 0','1,'+c))[::-1])])for c in'6278']and g
