# (decompressed)
def p(p):
	w,o=len,range;n=1
	while~-w({*p[n-1]}):n+=1
	u=[u[::n]for u in p[::n]];r=w(u);e=o(1,r);g,f=min((n,w)for n in e for w in e if u[n-1][w]*u[n][w-1]);e=-1,0,1;c=o(w(p));return[[p[w][o]or sum(u[g+c][f+d]*(u[w//n-c][o//n-d]==u[g][f])for c in e for d in e if-1<w//n-c<r>o//n-d>-1)for o in c]for w in c]
