p=lambda g:max((B:=[A for B in range(144)if all(map(sum,(A:=[A[B%12:][:3]for A in g[B//12:][:3]])+[*zip(*A)]))]),key=B.count)
