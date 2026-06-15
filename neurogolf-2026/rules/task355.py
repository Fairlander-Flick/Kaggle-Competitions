p=lambda g:[[sorted(range(10),key=lambda k:sum(A.count(k)-(k in A)*sum(k in A for A in zip(*g))for A in g))[1]]]
