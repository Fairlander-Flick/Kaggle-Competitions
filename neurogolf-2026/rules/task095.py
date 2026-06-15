p=lambda g:eval("[[r[i]|any((0,*r)[i:i+3])for i in range(9)]for r in zip(*"*2+"g)])]")
