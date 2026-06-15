p=lambda g,R=range(9):[[sum(g[a][b]**((i-a)**2+(j-b)**2)//5%25for a in R for b in R)for j in R]for i in R]
