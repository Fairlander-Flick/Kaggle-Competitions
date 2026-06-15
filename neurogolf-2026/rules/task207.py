p=lambda j:min((A:=[[j[B][A:A+2],j[B+1][A:A+2]]for B in[0,3]for A in[0,3]]),key=A.count)
