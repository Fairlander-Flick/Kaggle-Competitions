def p(a):a=sum(zip(*a),());A=a.count;B=max(map(A,{*a}-{0}));return[[*{C:0for C in a if A(C)==B}]]*B
