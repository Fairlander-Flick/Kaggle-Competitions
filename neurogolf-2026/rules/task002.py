p=lambda a,k=75:a*-k or p([[(v:=x or v&8,4-x//2)[k<1]for x in(8,)+r][:0:-1]for r in zip(*a)],k-1)
