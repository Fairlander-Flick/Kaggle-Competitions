p=lambda g:(A:=[[*map(min,(B:=[*map(min,*A)]),[9,9]+B[::-1])]for A in zip(g,zip(*g))])*(A==g)or p(A)
