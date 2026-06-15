p=lambda g,r=range(9):[g[A][:4]+[g[A-A%3-8][B-B%3-8]*g[A%3][B%3]for B in r]for A in r]
