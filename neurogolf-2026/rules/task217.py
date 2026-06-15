p=lambda g,r=range(9),m=max:[[m(m(g[A//3::3])[B//3::3])&m(m(g[A%3::3])[B%3::3])for B in r]for A in r]
