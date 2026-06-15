p=lambda j:[((0,4)*8)[(A:=max(j))>A[1::2]:][:len(A)]]*-~(B:=j.index(A))+j[B:-1]
