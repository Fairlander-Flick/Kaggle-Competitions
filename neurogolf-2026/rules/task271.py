p=lambda g:max((str(B:=[B[A%7:][:3]for B in g[A//7:][:3]]).count('1'),B)for A in range(49))[1]
