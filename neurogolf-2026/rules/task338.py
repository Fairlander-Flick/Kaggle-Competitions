p=lambda a,k=9:a*-k or p([[(v:=x or v&1,3*(x<1))[k<1]for x in(1,)+r][1:]for r in zip(*a)],k-1)
