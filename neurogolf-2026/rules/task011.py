p=lambda g,i=0,r=range(11):'8'in str((A:=[[[5,g[i&12|A>>2][i%3*4|B>>2]][A&3<3>B&3]for B in r]for A in r]))and p(g,i+1)or A
