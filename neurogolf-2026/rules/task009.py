p=lambda j,E=enumerate:[[max({*B[C::-3]}&{*B[C::3]}|{*D[:A:3]}&{*D[A::3]})for(C,D)in E(zip(*j))]for(A,B)in E(j)]
