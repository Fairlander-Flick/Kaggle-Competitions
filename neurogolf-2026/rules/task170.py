# (decompressed)
def p(r):o=[*map(any,r)];c=~-len(r)-o[::-1].index(1);d=[*map(bool,r[c])].index(1);a=r[c][d:].index(0);h=range(a);m=c-~-a;l=[*map(any,zip(*r[:m]))];t=sum(l)//a;return[[r[o.index(1)+c*t][l.index(1)+a*t]and r[m+c][d+a]for a in h]for c in h]
