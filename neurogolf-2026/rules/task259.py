p=lambda g,k=19:eval(f"{-k*g or p([*zip(*g[2>max(g[0]):][::-1])],~-k)}".replace(*'10'))
