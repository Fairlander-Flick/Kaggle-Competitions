p=lambda g,h=0:g[h:]and[max(g[h%3::3])]+p(g,h+1)
