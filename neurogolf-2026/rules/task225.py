p=lambda g,R=range(6):[[[g[C][D]+g[A+(C<A)][B+(D<B)]*(C-A&D-B&2>0)for D in R]for C in R]for A in R for B in R if g[A][B]][0]
