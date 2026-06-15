def p(g):A=len({0,*g[4]});C=range(5*A);D,E=g[0][1]<1,g[1][0]<1;return[[g[B//A][C//A]or 2*(B-C==A*(D-E)or-~B+C==A*(D+E+2))for C in C]for B in C]
