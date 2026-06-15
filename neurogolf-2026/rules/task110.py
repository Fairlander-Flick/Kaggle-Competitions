R=range(29);p=lambda g:next([[max(r[x]for r in g[y%Y::Y])or g[y][x+9]for x in R]for y in R]for Y in R[4:]if all(len({*c[i::Y]})<3for c in zip(*g)for i in R))
