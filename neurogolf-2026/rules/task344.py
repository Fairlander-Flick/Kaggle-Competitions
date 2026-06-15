p=lambda g,k=3:-k*g or p(eval(str([*zip(*g)][::-1]).replace('2, 3','0,8')),k-1)
