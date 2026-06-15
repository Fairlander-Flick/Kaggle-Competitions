def p(j):(A,B),(C,D)=[divmod(sum(j,[]).index(A),len(j[0]))for A in(3,4)];j[A][B]=0;j[A+(C>A)-(A>C)][B+(D>B)-(B>D)]=3;return j
