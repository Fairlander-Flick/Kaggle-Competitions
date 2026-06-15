p=lambda g:(A:=g[:3])*(A!=[*map(list,zip(*A))])or p(g[3:])
