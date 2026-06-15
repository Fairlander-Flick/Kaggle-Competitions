p=lambda a,k=1:-k*[*a]or p({a:0for a in zip(*a)if max(a)},k-1)
