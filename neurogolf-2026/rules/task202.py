p=lambda g:(A:=[[*map(min,*(A for A in g if max(A)in B))]for B in g])*(A!=A[::-1])or[*zip(*p([*zip(*g)]))]
