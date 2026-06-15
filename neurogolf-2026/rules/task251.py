p=lambda a,k=75:a*-k or p([[(v:=x or v&4,~-~x%3)[k<1]for x in(4,)+r][:0:-1]for r in zip(*a)],k-1)
