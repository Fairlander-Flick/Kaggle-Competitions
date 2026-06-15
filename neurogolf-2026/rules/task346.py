p=lambda g:[[min(sum(g,[]),key=lambda c:f"{g,*zip(*g)}".count(f"{c}, {c}"))]]
