p=lambda g,i=0:g[i]==g[0]and p(g,i+1)or[A[::~i]for A in g[::i+1]]
