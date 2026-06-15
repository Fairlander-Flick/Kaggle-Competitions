p=lambda g,e=enumerate:[[((A:=sorted((sum((B:=(abs(C-E),abs(D-G)))),~max(B)%2*A)for(E,F)in e(g)for(G,A)in e(F)if A))[0]<A[1][:1])*A[0][1]for(D,E)in e(D)]for(C,D)in e(g)]
