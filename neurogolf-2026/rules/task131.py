p=lambda g:(w:=len(g[0]))>(h:=len(g))and[*zip(*p([*map(list,zip(*g))]))]or'3'in str(C:=g[:g.index([2]*w)])and p(g[::-1])[::-1]or(C+[*filter(sum,g),[8]*w]+g[:1]*h)[:h]
