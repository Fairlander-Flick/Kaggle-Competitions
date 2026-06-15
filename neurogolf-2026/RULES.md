# NeuroGolf-2026 — TRUE RULES for all 400 tasks

Each task's rule is the **gold-medal Python solution** from the [SakanaAI Google Code Golf 2025](https://github.com/SakanaAI/google-code-golf-2025) entry. Those 400 ARC tasks are the **same 400** as NeuroGolf-2026 (`task001`=`007bbfb7`, identical ordering). Each `p=lambda ...` was **verified locally to reproduce every one of our grader's pairs** (train+test+arc-gen), so it is the true rule, not an overfit.

Columns: **pts** = our current ONNX base score (max 25; low = most room). `rule` = the transformation (golfed Python — read it as pseudocode). Full source per task in [`rules/`](rules/). Sorted lowest base score first.

> ONNX-golf tip: cost = mem+params; the win is to compute the rule on a **single-channel label grid `[1,30,30]`** and emit the 10-channel one-hot **only as the final (free) output** — never materialise a `[1,10,30,30]` intermediate.

| task | pts | shape | in→out | true rule (golfed Python) |
|--|--|--|--|--|
| **255** | 12.2 | same-shape | (30, 30)→(30, 30) | `# (decompressed) def p(e): 	m=n=h=l=a=b=0;x,f,u,y,g,=30,15,29,all,range 	d,i=lambda f:[[f[j][u-r]for j in g(x)]for r in g(x)],lambda f:[[f[u-j][r]for j in g(x)]for r in g(x)] 	f...` |
| **101** | 12.7 | same-shape | varies→varies | `# (decompressed) def p(n): 	p=enumerate;r={w+n*1j:a for(n,r)in p(n)for(w,a)in p(r)};t,c=({p for p in r if r[p]&t}for t in(1,2)) 	for i in c:t\|=c&{p+r for p in t for r in(1,1j,-1...` |
| **133** | 12.8 | same-shape | varies→varies | `# (decompressed) def p(u):  e,t,*o={(p,m):v for p,u in enumerate(u)for m,v in enumerate(u)if v},[]  def p(u):   if u in e:r[u]=e.pop(u);p((u[0]-1,u[1]));p((u[0]+1,u[1]));p((u[0]...` |
| **158** | 12.8 | same-shape | varies→varies | `# (decompressed) def p(n):o=max(n[0],key=n[0].count);f,=[r for a in(n,n[::-1])for g in range(len(n)-2)for h in range(len(n[0])-2)if len(set(r:=[a[g+p//3][h+p%3]for p in range(9)...` |
| **096** | 13.0 | shape-changes | varies→varies | `# (decompressed) from re import* def p(i,z=range):  r=sub(', ','',str(i+[*zip(*i)]));r+=r[::-1];i=int(max(r,key=r.count));l={0:(0,i)}  for m in z(10):   if(i^m)*(e:=findall(f'{m...` |
| **286** | 13.1 | same-shape | varies→varies | `import re p=lambda g:exec('g[:]=zip(*eval(re.sub("0(?=, ([^08]))",r"%d-\\1",str(g)))[::-1]);'%(sum({*sum(g,[])})-8)*444)or g` |
| **367** | 13.1 | same-shape | varies→varies | `p=lambda g,b=bytes,e=enumerate:(B:=[*map(b,g)],E:=[*map(b,zip(*g))])and[[v or~(d:=E[a].rfind(5,0,r))&~(f:=E[a].find(5,r))and 4&min(B[f][(l:=-~B[d].rfind(0,0,a)):(h:=B[d].find(0,...` |
| **233** | 13.3 | shape-changes | varies→varies | `# (decompressed) def p(b,g=2,v={}):  n=range(9)  for y in range(len(b)-2):   for x in range(len(b[0])-2):    u=bytes(b[y+i//3][x+i%3]==g&2 for i in n)    if g&2 and(r:=sum(l:={b...` |
| **285** | 13.4 | same-shape | varies→varies | `# (decompressed) def p(l): 	p,h=range,eval(str(l));d=p(len(l)-1) 	def f(a,r,x): 		try:1/(h[a][r]==n[x]>0);h[a][r]=0;[(s>>2 or l[(a,z-~z-a)[s>1]].__setitem__((r,t-~t-r)[s&1],n[x^...` |
| **018** | 13.4 | same-shape | varies→varies | `# (decompressed) def p(u): 	e=len;n,r=e(u),e(u[0]);g=set();s=lambda i,o:n>i>-1<o<r and(e:=u[i][o])and(exec('u[i][o]=0')or[(e,i,o)]+s(i+1,o)+s(i-1,o)+s(i,o+1)+s(i,o-1))or[] 	for ...` |
| **118** | 13.4 | same-shape | varies→varies | `# (decompressed) def p(p):  t={(l,n)for l in range(len(p))for n in range(len(p[0]))if p[l][n]&2};d=lambda i,l:[i and(d(i[1:],l)or not i[0]&l and d(i[1:],l\|i[0])),l][t<=l]  for n...` |
| **110** | 13.5 | same-shape | (29, 29)→(29, 29) | `R=range(29);p=lambda g:next([[max(r[x]for r in g[y%Y::Y])or g[y][x+9]for x in R]for y in R]for Y in R[4:]if all(len({*c[i::Y]})<3for c in zip(*g)for i in R))` |
| **366** | 13.5 | shape-changes | varies→varies | `# (decompressed) def p(r):g=len(r)>len(r[0]);n=[*map(list,(r,zip(*r))[g])];f,o=len(n),len(n[0])>>1;i,r=sorted([[r[:o]for r in n],[r[o:]for r in n]],key=lambda r:len(set(sum(r,[]...` |
| **002** | 13.5 | same-shape | varies→varies | `p=lambda a,k=75:a*-k or p([[(v:=x or v&8,4-x//2)[k<1]for x in(8,)+r][:0:-1]for r in zip(*a)],k-1)` |
| **029** | 13.5 | shape-changes | varies→varies | `p=lambda g,k=9:(A:=[*filter((B:={k}.issubset),zip(*filter(B,g)))])and{*A[0]}=={k}and[*zip(*A[1:~0])][1:~0]or p(g,~-k)` |
| **077** | 13.5 | same-shape | varies→varies | `# (decompressed) def p(e,s=enumerate):  m=v={(m,n)for m,v in s(e)for n,r in s(v)if r==2}  for x in m:m={(v,r)for v,n in m for r,f in m if-3<r-v<3>f-n>-3 for v in range(min(v,r),...` |
| **064** | 13.6 | same-shape | varies→varies | `p=lambda g:exec('*_,d,e=sorted(range(10),key=sum(g,[]).count)\n'+'for a in g:\n for b in range(1,bytes(a).find(d)):a[b]=a[b-(a[b]==e)]\ng[:]=map(list,zip(*g[::-1]))\n'*4)or g` |
| **054** | 13.6 | same-shape | (30, 30)→(30, 30) | `# (decompressed) def p(d): 	u=eval(str(d));g=d[0][0];a=f=range(30);w={(w,j)for w in a for j in a if d[w][j]^g};e=w\|w 	while e: 		r=[e.pop()] 		for n,i in r:y=e&{(n+1,i),(n-1,i),...` |
| **159** | 13.6 | shape-changes | varies→varies | `def p(g):A=str(g).count('2')>>2;B=lambda A:[*zip(*[A for A in A if~2&max(A)])];C=range(-~A);return[[2*(D%A*(C%A)<1)or B(B(g))[D*3//A][C*3//A]for C in C]for D in C]` |
| **208** | 13.6 | same-shape | (21, 21)→(21, 21) | `# (decompressed) def p(a): 	o=sum(a,[]);c=o.count;k=min(o,key=c);u=~-sum(k in r for r in a);i=c(k)//2-u 	for s in range(21-u): 		for e in range(21-i):sum(sum(r[e+1:e+i])for r in...` |
| **005** | 13.6 | same-shape | (21, 21)→(21, 21) | `# (decompressed) def p(m):  r=range;f=max(([(i,y)for d in r(9)if m[(i:=t//19+d//3)][(y:=t%19+d%3)]]for t in r(361)),key=len)  for t in r(45):   t,n,u=t%3*4-4,t//15*4-4,t%5+1   f...` |
| **173** | 13.6 | same-shape | varies→varies | `# (decompressed) def p(n):[((r:=[n[y+f//3][t+f%3]for f in range(9)])==r[::-1])*r[4]*any(r[:4])*(r[4]==n[l+1][d+1]or sum(n[l+f//3][d+f%3]==r[f]for f in range(9))==8)and exec('for...` |
| **187** | 13.7 | same-shape | varies→varies | `p=lambda a,k=75:a*-k or p([[A:=B or(2,3*(A==3))[k>0]for B in(3,)+B][:0:-1]for B in zip(*a)],k-1)` |
| **398** | 13.7 | shape-changes | (1, 5)→varies | `def p(g):A,=g;g=5*len({*A}-{0});return[(([0]*~-g+A)*2)[B:B+g]for B in range(g)]` |
| **209** | 13.7 | shape-changes | varies→varies | `# (decompressed) def p(o,y=enumerate):  (e,z),*a,(c,a)=[(c,x)for c,n in y(o)for x,a in y(n)if a&4]  g=[(a,t,u)for t,n in y(o[c+1:])for a,u in y(n)if u]  o=[n[z:a+1]for n in o[e:...` |
| **363** | 13.7 | same-shape | (10, 10)→(10, 10) | `# (decompressed) def p(r,u=10): 	a=range(u*u);f,n=[{(q//u,q%u)for q in a if r[q//u][q%u]==f}for f in(2,0)];p,c=map(min,zip(*f));i=[q for q in a if(i:={(q//u+j-p,q%u+w-c)for j,w ...` |
| **036** | 13.7 | shape-changes | (30, 30)→varies | `p=lambda g,c=1:(A:=[A for A in zip(*(A for A in g if c in A))if c in A])and len(A)<6>len(A[0])and[*zip(*A)]or p(g,-~c)` |
| **201** | 13.7 | shape-changes | (13, 13)→varies | `# (decompressed) def p(c,p=enumerate):(o,i),*m,(n,d)=[(e,f)for e,r in p(c)for f,m in p(r)if m==4];u=[(f,m,e)for e,r in p(c)for f,m in p(r)if m*(e-o\|n-e\|f-i\|d-f<0)];m,a,e=u[0];re...` |
| **264** | 13.7 | shape-changes | varies→(9, 9) | `p=lambda g,r=range:[[max(g[C+A%3][D+B%3]*(sum(1<<A for A in r(9)if g[C+A//3][D+A%3]-5)==ord('+7Fy Ŕèǰǀ'[A-A%3+B//3])-32)for C in r(len(g)-2)for D in r(len(g[0])-2))for B in r(9)...` |
| **025** | 13.7 | same-shape | varies→varies | `p=lambda g:any(B:=(*map(min,*g),0))*[[B[A+(0<B[A+1]in C[:A])-(0<B[A-1]in C[A:])]for A in range(len(C))]for C in g]or[*zip(*p([*zip(*g)]))]` |
| **076** | 13.7 | same-shape | varies→varies | `# (decompressed) def p(g):  e=enumerate;a={h+1j*i:y for h,i in e(g)for i,y in e(i)if y};e=[min(a,key=a.get)];d=0  for y in e:e+=[n for n in a if(abs(n-y)<2)>(n in e)];d+=y*(a[y]...` |
| **364** | 13.8 | same-shape | varies→varies | `def p(g): 	F=enumerate;B={C\|A<<5for(A,B)in F(g)for(C,D)in F(B)if D};G=B\|B 	while B: 		H,*C=-1,B.pop() 		for A in C:D={A+1,A-1};E=D\|{A+32,A-32};H+=len(G&D)*len(G&E-D);C+=B&E;B-=E...` |
| **157** | 13.8 | same-shape | (10, 15)→(10, 15) | `# (decompressed) def p(n):p,i,*r=range,15;m=sum(n,[]);n=[[]];[(n:=[n+[(f,r)]for n in n for f in p(45)if m[f]<1],r:=[])for f in p(16)if r==(r:=r+[p for p in p(f,150,i)if(i>f)&m[p...` |
| **175** | 13.8 | same-shape | (21, 21)→(21, 21) | `p=lambda g,r=range(2,23):[[1+(A//B+B//A+g[0][0]-3)%max(sum(g,[]))for B in r]for A in r]` |
| **107** | 13.8 | shape-changes | (5, 5)→varies | `def p(g):A=len({0,*g[4]});C=range(5*A);D,E=g[0][1]<1,g[1][0]<1;return[[g[B//A][C//A]or 2*(B-C==A*(D-E)or-~B+C==A*(D+E+2))for C in C]for B in C]` |
| **216** | 13.8 | shape-changes | (20, 20)→varies | `p=lambda a,e=enumerate:min((-str(C:=[B[A:(*E,0).index(0,A)]for B in a[B:(*D,0).index(0,B)]]).count('2'),B,A,C)for(A,D)in e(zip(*a))for(B,E)in e(a))[3]` |
| **379** | 13.8 | same-shape | varies→varies | `# (decompressed) def p(e):  p=8in e[0];e=(e,[*map(list,zip(*e))])[p];f=[z for z,r in enumerate(e)if r[0]]*2  for z,r in enumerate(e):   for t,r in enumerate(r):    for a in f[z>...` |
| **069** | 13.8 | same-shape | (10, 10)→(10, 10) | `def p(a): 	C=range(100);A=sum(a,[]);a=A*1;D=[B for B in C if A[B]&7] 	for E in C: 		for B in D*(a[E]==8):a[B],a[E+B-D[0]]=0,A[B] 	return[*zip(*[iter(a)]*10)]` |
| **066** | 13.9 | same-shape | varies→varies | `# (decompressed) def p(z):  b=len(z);s=sum(z,[]);l=lambda m:[*map(list,zip(*m))];r=lambda*m:range(min(m),-~max(m));(i,f),(u,e)=n=[divmod(s.index(m),b)for m in(2,3)]  if z[i][f+1...` |
| **243** | 13.9 | same-shape | varies→varies | `p=lambda g,k=99:g*-k or p([[a:=r or a==1for r in(2,)+r][:0:-1]for r in zip(*g)],k-1)` |
| **126** | 13.9 | same-shape | varies→varies | `p=lambda g:g[:-1]+[[4*(0<sum(A)in A)for A in zip(*g)]]` |
| **191** | 13.9 | same-shape | (23, 23)→(23, 23) | `# (decompressed) def p(n):  y=lambda n:1in n;e=[*zip(*filter(y,zip(*filter(y,n))))];y=enumerate;c=[[0,*n,0]for n in[[0]*23,*n,[0]*23]]  for r in[0]*4:   for r in e,e[::-1]:    f...` |
| **280** | 13.9 | same-shape | varies→varies | `def p(a,k=3): 	for(A,D)in enumerate(zip(*a)): 		C=-~bytes(D).find(b'\x00\x02');B=(*D[C:],0).index(0) 		for E in a[:C]:E[A-B+1:A+B]=a[C][A-B+1:A+B] 	return-k*a or p([*map(list,zi...` |
| **145** | 13.9 | same-shape | varies→varies | `def p(a): 	A=len(a[0]);F=len(a)*A;G,D=0,3;B=lambda i:i<F and(C:=a[i//A])[j:=i%A]==G and(C.__setitem__(j,D)or-~B(i+A)+B(i+(A>j+1)));E=[(C,A)for A in range(F)if(C:=B(A))];G=D 	for...` |
| **205** | 13.9 | shape-changes | varies→varies | `p=lambda g,r=range,l=len:max((l(str(B)),[[max({*A,*B}-{A[0]}or A)for B in zip(*B)]for A in B])for C in r(l(g))for A in r(l(g[0]))for D in r(C*A)if l({*str((B:=[B[D%A:A]for B in ...` |
| **165** | 13.9 | same-shape | (20, 20)→(20, 20) | `def p(g): 	B=sum(g,[]);*E,C=filter(int,B) 	for A in range(380): 		for D in g[A//20+1:]*(B[A+20]^B[A])*(0<B[A]!=C):D[A%20]=max(B[A+20::20]) 	return g` |
| **306** | 13.9 | same-shape | varies→varies | `p=lambda g,o=lambda x:[*zip(*[max(x[A%10::10])for A in range(len(x))])]:o(o(g))` |
| **382** | 13.9 | same-shape | varies→varies | `def p(g): 	for A in(0,1)*4: 		B,*C=g=(g[::-1],[*map(list,zip(*g))])[A];A=0 		for D in C*(('[2'in str(g))-('8'in str(C))):A+=D[0]>1;D[A:]=B[:-A]or B 	return g` |
| **238** | 13.9 | shape-changes | varies→varies | `def p(I):C=filter;D={8}.issubset;E,F,G,H={}.fromkeys(C((7).__and__,sum(I,[])));J=[*C(D,zip(*C(D,I)))];A=len(J);K=range(A);B=[0];return[B+[E]*A+B,*[[F,*[J[B][C]and((F,E,H,G)[(C<B...` |
| **234** | 14.0 | same-shape | varies→varies | `p=lambda g,k=3:-k*g or p([*zip(*[A for A in g[:1]*12+g if A.count(max(max(g,key=any)))^1][:~len(g):-1])],k-1)` |
| **170** | 14.0 | shape-changes | varies→varies | `# (decompressed) def p(r):o=[*map(any,r)];c=~-len(r)-o[::-1].index(1);d=[*map(bool,r[c])].index(1);a=r[c][d:].index(0);h=range(a);m=c-~-a;l=[*map(any,zip(*r[:m]))];t=sum(l)//a;r...` |
| **219** | 14.0 | same-shape | (15, 10)→(15, 10) | `# (decompressed) def p(o):  f=enumerate;p=[];m=-2  for r,n in f(o):   if any(n):p+=[set()]*(r-1>m);p[-1]\|={(r,n)for n,a in f(n)if a};m=r  g,*e=p  for e in e:   for r,n in max((l...` |
| **071** | 14.0 | same-shape | (16, 16)→(16, 16) | `p=lambda g:[[(A:=max((B:=bytes(max(g,key=any)))))*(A in[C[D],C[B.find(A)+B.rfind(A)-D&15]])for D in range(16)]for C in g]` |
| **023** | 14.0 | same-shape | varies→varies | `def p(g):B=len(g[0]);D=lambda a:a<{1}or any(D(a-C)*[g[A//B].__setitem__(A%B,6*len(C)-16)for A in C]for A in a for C in({A,A+1,A+2},{A,A+B,A+B*2},{A,A+1,A+B,A-~B})if C<=a);D({A f...` |
| **090** | 14.0 | same-shape | varies→varies | `def p(a,r=range): 	*_,C,A,B=min((any(any(A[D:B])for A in a[C:A]),(C-A)*(B-D),a[C:A],D,B)for A in r(-~len(a))for C in r(A-1)for B in r(-~len(a[0]))for D in r(B)) 	for D in C:D[A:...` |
| **112** | 14.0 | same-shape | varies→varies | `p=lambda g,i=0,e=enumerate:3in g[i]and[[C\|2&g[min(A,i-~i-A)][min(B,2*g[i].index(3)+1-B)]for(B,C)in e(B)]for(A,B)in e(g)]or p(g,-~i)` |
| **088** | 14.0 | shape-changes | varies→varies | `p=lambda g,k=87:-k*[[A and g[0][0]for A in A[1:-1]]for A in g[1:-1]]or p([*zip(*g[1-any(g[0]):][::-1])],k-1)` |
| **222** | 14.0 | same-shape | (16, 16)→(16, 16) | `p=lambda g,k=2:g*-k or p([[A*(A in B[C-1:C+2:2],sum(g,[]).count(A)>8)[k<1]for(C,A)in enumerate(B)]for B in(zip(*g),g)[k<1]],k-1)` |
| **137** | 14.0 | same-shape | varies→varies | `def p(g):A=range(len(g));E,(B,C),D=[(B,C)for B in A for C in A if g[B][C]];return[[g[B][C]*(max(D-B,B-D,A-C,C-A)%(B-E[0])<1)for A in A]for D in A]` |
| **284** | 14.0 | same-shape | varies→varies | `# (decompressed) def p(a):h=enumerate;(u,c,o),(e,n,v)=((u,c,t)for(u,e)in h(a)for(c,t)in h(e)if t);return[[(o,v)[(t:=(b+b-u-e,h+h-c-n)[u==e])>0]*((i:=(h-c,b-u)[u==e]**2)<9==t*t o...` |
| **313** | 14.1 | same-shape | varies→varies | `p=lambda g,l=len:[(A[1:l({*A})]*9)[:l(A)]for A in g[:2]*99][:l(g)]` |
| **370** | 14.1 | same-shape | varies→varies | `def p(a): 	A=sum(a,[]);B=len(a[0]);G=sum({*A})-A[0];I,C=divmod(A.index(G),B);H=[(A//B,A%B)for(A,C)in enumerate(A)if 1>C];L,J,K=max((D*D,D,C-A)for(B,A)in H if(D:=I-B)in(C-A,A-C))...` |
| **033** | 14.1 | same-shape | (17, 17)→(17, 17) | `p=lambda g,r=range(17):[[g[A][B]or g[A%6][B%6]and g[5][0]for B in r]for A in r]` |
| **193** | 14.1 | same-shape | varies→varies | `p=lambda i,k=1:-k*i or p([[B&(A\|C)for(A,B,C)in zip((0,)+A,A,A[1:]+(0,))]for A in zip(*i)],k-1)` |
| **097** | 14.1 | same-shape | varies→varies | `p=lambda a,e=enumerate:[[C*(C<sum(sum([0,*A][B:B+3])for A in[[],*a][A:A+3]))for(B,C)in e(B)]for(A,B)in e(a)]` |
| **203** | 14.1 | same-shape | varies→varies | `p=lambda g:[[g[(B:=len(g)>>1)][B+A.index(C)]for C in A]for A in g]` |
| **011** | 14.1 | same-shape | (11, 11)→(11, 11) | `p=lambda g,i=0,r=range(11):'8'in str((A:=[[[5,g[i&12\|A>>2][i%3*4\|B>>2]][A&3<3>B&3]for B in r]for A in r]))and p(g,i+1)or A` |
| **162** | 14.1 | same-shape | (20, 20)→(20, 20) | `def p(g,k=323): 	k and p(g,k-1);A=g[k//18:][:3];k%=18 	for B in A*all(1>max(A[k:k+3])for A in A):B[k:k+3]=1,1,1 	return g` |
| **020** | 14.1 | same-shape | (10, 10)→(10, 10) | `def p(g,E=enumerate): 	P=[(r,c,v)for(r,R)in E(g)for(c,v)in E(R)if v];a,b,_=map(min,zip(*P)) 	for(r,c,v)in P:exec('r,c=a+b+4-c,b-a+r;g[r][c]=v;'*3) 	return g` |
| **192** | 14.1 | same-shape | varies→varies | `p=lambda g,d=enumerate:[[(A:=max(range(1,10),key=sum(g,[]).count))*(A in B[:C+2][-3:]*E*(A in[*zip(*g[:D+2])][C][-3:]))for(C,E)in d(B)]for(D,B)in d(g)]` |
| **275** | 14.2 | shape-changes | varies→varies | `def p(j):A=len(j[:len(j[0])]);B=range(A*A);return[[sum(j[C%A+B-A][D%A+B-A]//8*j[C//A-B][D//A-B]for B in(0,A))for D in B]for C in B]` |
| **340** | 14.2 | same-shape | varies→varies | `p=lambda g:exec('for r in g:r[r[0]in r[1:]]\|=r[0]\ng[:]=map(list,zip(*g[::-1]))\n'*4+'for r in g[2:-2]:r[2:-2]=[0]*(len(r)-4)')or g` |
| **037** | 14.2 | same-shape | (10, 10)→(10, 10) | `def p(g): 	for B in(C:=sum(g,[])): 		A=C.index(B) 		while C[(A:=A+11-2*(B in C[A+9::9]))]<B:g[A//10][A%10]=B 	return g` |
| **253** | 14.2 | shape-changes | (13, 13)→(4, 4) | `p=lambda g,w=range(4):[[{A.index(0):max(A)for(B,C)in zip(g,g[1:])for A in zip(C[1:],C,B[1:],B)if A.count(0)<2}[A&2\|B>>1]*(A*B%3<1)for B in w]for A in w]` |
| **138** | 14.2 | shape-changes | varies→varies | `p=lambda g,k=5:-k*g or p(k//4*[*zip(*g[(B:=bytes(map(all,g))).find(1):-~B.rfind(1)])]or[A[:1]*(B:=-~bytes(A).rfind(A[0]))+A[B:]for A in zip(*g[::-1])],k-1)` |
| **085** | 14.2 | same-shape | varies→varies | `p=lambda g,c=0,a=0:g and[((A:=g.pop(0)),[(a:=~a&A)for A in A])[g[:1]==[c]]]+p(g,A)` |
| **182** | 14.2 | same-shape | (20, 20)→(20, 20) | `def p(i): 	c=sum(i,[]);d,e={},0 	for g in c: 		f=b=();h=[e] 		for a in h: 			if c[a]%5:c[a]=0;f+=a,;b+=a-e,;h+=a-1,a+1,a+20 		d[b]=d.get(b,f)+f;e+=1 		if g&2:j,k=g,b 	for x in d...` |
| **009** | 14.2 | same-shape | varies→varies | `p=lambda j,E=enumerate:[[max({*B[C::-3]}&{*B[C::3]}\|{*D[:A:3]}&{*D[A::3]})for(C,D)in E(zip(*j))]for(A,B)in E(j)]` |
| **204** | 14.2 | same-shape | varies→varies | `import re s=re.sub p=lambda g:eval(s('(?<!1, )1(, 0)+, 1',lambda m:s('0','27'[len(m[0])%2],m[0]),str(g)))` |
| **198** | 14.2 | same-shape | varies→varies | `# (decompressed) def p(u,a=len): 	g=a(u) 	def w(p,n): 		if-1<p<g>n>-1<1>u[p][n]:o[p,n]=r[p]=f[n]=u[p][n]=4;w(p+1,n);w(p-1,n);w(p,n+1);w(p,n-1) 	for e in range(g*g): 		o,r,f={},{...` |
| **335** | 14.3 | same-shape | varies→varies | `def p(g): 	(A,B),(C,D)=[divmod(sum(g,[]).index(A),len(g[0]))for A in[8,2]] 	while A-C:A+=A<C or-1;g[A][B]=4 	g[C][B:D:D>B or-1]=[4]*abs(B-D);return g` |
| **089** | 14.3 | same-shape | (13, 13)→(13, 13) | `# (decompressed) def p(w): 	s=range(13) 	for n in 3,2: 		b={(u,i)for u in s for i in s if w[u][i]==n} 		for k in b: 			l=[k] 			for e,f in l:l+=[(u,i)for r in range(9)if(u:=e+r/...` |
| **092** | 14.3 | same-shape | varies→varies | `p=lambda g,s=lambda h:[[C or sum({*A[:B]}&{*A[B:]})for(B,C)in enumerate(A)]for A in zip(*h)]:s(s(g))` |
| **224** | 14.3 | same-shape | varies→varies | `def p(g,k=3,e=enumerate):D,A,E=zip(*((B,D,A)for(B,C)in e(g)for(D,A)in e(C)if A));B,C=-~min(A),max(A);g[-~D[0]][B:C]=[sum({*E})-5]*(C-B);return-k*g or p([*map(list,zip(*g[::-1]))...` |
| **338** | 14.3 | same-shape | varies→varies | `p=lambda a,k=9:a*-k or p([[(v:=x or v&1,3*(x<1))[k<1]for x in(1,)+r][1:]for r in zip(*a)],k-1)` |
| **328** | 14.3 | same-shape | varies→varies | `p=lambda g,e=enumerate:[[((A:=sorted((sum((B:=(abs(C-E),abs(D-G)))),~max(B)%2*A)for(E,F)in e(g)for(G,A)in e(F)if A))[0]<A[1][:1])*A[0][1]for(D,E)in e(D)]for(C,D)in e(g)]` |
| **131** | 14.3 | same-shape | varies→varies | `p=lambda g:(w:=len(g[0]))>(h:=len(g))and[*zip(*p([*map(list,zip(*g))]))]or'3'in str(C:=g[:g.index([2]*w)])and p(g[::-1])[::-1]or(C+[*filter(sum,g),[8]*w]+g[:1]*h)[:h]` |
| **349** | 14.3 | same-shape | varies→varies | `def p(I): 	h=len(I);g=eval(str(I));r=range 	for k in r(h*h): 		y,x=k//h,k%h;k=[*I[y],0].index(0,x);t=k-x>>1 		for j in r(y-t,h): 			for i in r(x-t,k+t): 				if j>-1<i<h:g[j][i]\|...` |
| **325** | 14.3 | shape-changes | varies→varies | `def p(g):C=enumerate;A={D+A*1j:E for(A,B)in C(g)for(D,E)in C(B)};B=lambda z:A.pop(z,0)and B(z+1)\|B(z-1)\|B(z+1j)\|B(z-1j)\|1;A=sum(map(B,A\|A));return[[0]*B+[8]+[0]*(A+~B)for B in r...` |
| **004** | 14.4 | same-shape | varies→varies | `p=lambda j:[exec('i-=1;v,a[i]=a[i],0;a[i+any(b[i+1:])]+=v;'*(i:=len(a)))for(a,b)in zip(j,j[1:])]and j` |
| **080** | 14.4 | same-shape | varies→varies | `# (decompressed) def p(p): 	w,o=len,range;n=1 	while~-w({*p[n-1]}):n+=1 	u=[u[::n]for u in p[::n]];r=w(u);e=o(1,r);g,f=min((n,w)for n in e for w in e if u[n-1][w]*u[n][w-1]);e=-...` |
| **358** | 14.4 | same-shape | varies→varies | `p=lambda g,k=1:g*-k or p([*zip(*((A:=[*filter(None,B)])[1:]and(A*7)[-B.index(A[0]):]+A*7or B for B in g))],~-k)` |
| **128** | 14.4 | same-shape | (15, 15)→(15, 15) | `p=lambda g:[*zip(*(A[-A.count(0):]+A for A in zip(*g)))][:15]` |
| **070** | 14.4 | same-shape | (17, 17)→(17, 17) | `p=lambda g:[[b\|2&-b*(8in a)*any(8in r[:-~j]for r in g)*any(8in r[j:]for r in g)for j,b in enumerate(a)]for a in g]` |
| **265** | 14.4 | same-shape | (18, 18)→(18, 18) | `p=lambda g,k=18:g*(k<2)or(G:=eval(str(g)),[exec('r[j:j+2]=2,2')for i in range(19-k)for j in range(17)if 1>max(t[j]\|t[j+1]for t in G[i:i+k])for r in g[i:i+k]],p(g,k-1))[2]` |
| **014** | 14.4 | shape-changes | varies→varies | `p=lambda j,f=filter:[*zip(*f((A:={min({*(B:=sum(j,[]))}-{0},key=B.count)}.issubset),zip(*f(A,j))))]` |
| **378** | 14.4 | same-shape | varies→varies | `def p(a,k=3):C=range(len(a)-2);[exec('a[A+~D][B+~D]=a[A+2][B+2]')for A in C for B in C if(R:=a[A+1])[B+1]<a[A][B]==R[B]==a[A][B+1]for D in C[:A][:B]];return-k*a or p([*map(list,...` |
| **383** | 14.4 | same-shape | varies→varies | `def p(g):A,F,E,*G,H,G=filter(any,g);B=max(A);C=A.index(B);D=E[C+2];return[[(F,(D,B)[F>0])[D in E[-~C::sum(A)//B-3]+G]for(F,*G)in zip(E,F,H)]for E in g]` |
| **044** | 14.4 | same-shape | (10, 10)→(10, 10) | `# (decompressed) i=range(100) def p(w):  a=sum(w,[])  for d in a:   n=[w for w in i if a[w]==d]   r=next((t for t in i if all(a[(x:=w-n[0]+t):x+1]<[1]*all(w+t in n or a[x+t:][:1...` |
| **215** | 14.5 | same-shape | varies→varies | `p=lambda g,h=0:g[h:]and[max(g[h%3::3])]+p(g,h+1)` |
| **252** | 14.5 | same-shape | varies→varies | `p=lambda g:[[(A,4)[A>0<B&1]for(B,A)in enumerate(A)]for A in g]` |
| **213** | 14.5 | shape-changes | varies→varies | `p=lambda a:[*zip(*(a[len(A:=[B for A in a for B in{*A}-{0,5}]):]and[A]*len(A)or p([*zip(*a)])))]` |
| **384** | 14.5 | shape-changes | (9, 9)→varies | `p=lambda g,f=lambda a:sum(([A]*2*any(A)for A in zip(*a)),[]):f(f(g))` |
| **396** | 14.5 | shape-changes | varies→varies | `# (decompressed) p=lambda p,r=range:min((u-i+b-n,[[i and sum({*sum(p,[])})-d for i in i[b:n+1]]for i in p[u:i+1]])for i in r(len(p))for n in r(len(p[0]))for u in r(i)for b in r(...` |
| **221** | 14.5 | shape-changes | (3, 3)→varies | `def p(a):A=f"{a}".count('0');return[(C*(9+A*~B)+[0]*27)[:3*A]for B in range(A)for C in a]` |
| **202** | 14.5 | same-shape | varies→varies | `p=lambda g:(A:=[[*map(min,*(A for A in g if max(A)in B))]for B in g])*(A!=A[::-1])or[*zip(*p([*zip(*g)]))]` |
| **324** | 14.5 | same-shape | varies→varies | `# (decompressed) p=lambda a:(t:=enumerate,n:=sum(a,[]),n:=sorted({*n},key=n.count)[-2:],u:=[(m,e)for m,e in t(a)for e,p in t(e)if{p}-{*n}],f:=[sum({*e}&{*n})%sum(n)for e in a+[*...` |
| **351** | 14.5 | shape-changes | (16, 16)→(5, 5) | `p=lambda g:[(A:=sum(g,[]))[~A.index(3)-16*B::-1][:5]for B in range(5)]` |
| **400** | 14.5 | shape-changes | (24, 24)→(5, 5) | `p=lambda g:[g[~g.index(A)][~A.index(1)::-1][:5]for A in g if 1in A]` |
| **185** | 14.5 | shape-changes | varies→(3, 3) | `def p(g): 	A={*g[0]};B=zip 	for C in A:g=[B for B in B(*g)if{*B}-A] 	return[[B*(B==C==D==E!=sum(A))for(B,C,D,E)in B(C,C[1:],D,D[1:])]for(C,D)in B(g,g[1:])]` |
| **065** | 14.5 | shape-changes | varies→varies | `def p(g):A=len(g)//2;B=0,-~A;C=[[B[D:D+A]for B in g[C:C+A]]for C in B for D in B];return min(C,key=C.count)` |
| **387** | 14.6 | same-shape | varies→varies | `def p(g,A=enumerate):(G,C),*B,(H,D)=I=[(B,D)for(B,C)in A(g)for(D,E)in A(C)if E];return[[J+5*((E:=min(A-C,D-A))*(F:=min(B-G,H-B))<1<E\|F<E\|F^1)or max(g[E][C^D^F]*(2>A-F>-2<B-E<2)f...` |
| **177** | 14.6 | shape-changes | varies→varies | `p=lambda g:[A[::-1]for B in g if(A:=[*filter(int,B)])]` |
| **017** | 14.6 | same-shape | (21, 21)→(21, 21) | `p=lambda g,l=4,R=range(21):max(g,key=all)in(A:=[[max(max(A[B%l::l])for A in g[A%l::l])for B in R]for A in R])and A or p(g,-~l)` |
| **377** | 14.6 | shape-changes | varies→varies | `p=lambda g,f=lambda d,x=0:[*zip(*[x:=b for b in d if x!=b])]:f(f(g))` |
| **319** | 14.6 | shape-changes | varies→varies | `# (decompressed) def p(g):f=sum(g,[]);m=max;t=f.count;z=m(f,key=t);d={v:[divmod(n,len(g[0]))for n,e in enumerate(f)if e==v]for v in{*f}-{z}};a=m(d,key=t);f=m(d,key=lambda u:(m(m...` |
| **231** | 14.6 | shape-changes | varies→varies | `p=lambda g:[(r[:6]*9)[:len(r)*2]for r in g]` |
| **174** | 14.6 | shape-changes | (10, 10)→varies | `p=lambda g,c=9,f=filter:[*zip(*(A:=[*f((B:={c}.issubset),zip(*f(B,g)))]))]*(A==A[::-1])or p(g,~-c)` |
| **196** | 14.6 | same-shape | varies→varies | `p=lambda d,k=51:-k*d or p([[B^2*[A==2,(k<7>C<1)\|A>2,k<1,0][B]for(A,B,C)in zip((2,)+A,A,A[1:]+(1,))]for A in zip(*d[::-1])],k-1)` |
| **288** | 14.6 | same-shape | varies→varies | `def p(g):B=A=g[-2].count(0)//2;exec('A-=1;C=g[A-B-2];C[A]=C[~A]=g[-1][B];'*A);return g` |
| **244** | 14.6 | shape-changes | varies→varies | `p=lambda g,i=0:g[i]==g[0]and p(g,i+1)or[A[::~i]for A in g[::i+1]]` |
| **046** | 14.6 | shape-changes | varies→varies | `def p(g): 	E=[];A=[];C=D=0;B=0,0,0 	for F in(*zip(*g),B): 		if F>B:A+=F, 		elif A:C+=D and D.index(5)-A[0].index(5);E+=[[C and-5+sum({*sum(A,B)})for C in(B+D+B)[3-C:6-C]]for D i...` |
| **392** | 14.7 | same-shape | (10, 10)→(10, 10) | `p=lambda g,r=range(10):[[((A:=max(max(g))),5,5)[min(max(C-A,A-C,D-B,B-D)for A in r for B in r if g[A][B])%(3-(f"{A}, 0, {A}"in f"{g}"))]for D in r]for C in r]` |
| **063** | 14.7 | same-shape | varies→varies | `p=lambda g:[[B or 3-3*any(A[1:~0])*any(C)for(B,D,*C,E)in zip(A,*g)]for A in g]` |
| **161** | 14.7 | same-shape | varies→varies | `p=lambda g:[[(A:=min(A:=sum(g,[]),key=A.count))*(A in[B[0],C])for C in g[0]]for B in g]` |
| **154** | 14.7 | same-shape | (15, 15)→(15, 15) | `p=lambda g,k=3:-k*g or p([A[(B:={2,5}<{*A}and 2*A.index(2))::-1]+A[B+1:]for A in zip(*g[::-1])],k-1)` |
| **278** | 14.7 | same-shape | varies→varies | `p=lambda i,k=3,e=enumerate:-k*i or p([*zip(*[[C or 3*('2, 2'in str([A[B-2:B+3]for A in[[],*i][A:A+3]]))for(B,C)in e(B)]for(A,B)in e(i)][::-1])],k-1)` |
| **359** | 14.7 | same-shape | varies→varies | `p=lambda d:[[max(S:=r+C,key=S.count)for*C,in zip(*d)]for r in d]` |
| **368** | 14.7 | same-shape | (10, 10)→(10, 10) | `def p(j,B=range(100)): 	A=sum(j,[]);C=[B for B in B if A[B]%5] 	for D in B: 		for E in C*(A[D]==5):A[D+E-C[0]]=A[E] 	return[A[B:B+10]for B in B[::10]]` |
| **232** | 14.7 | same-shape | varies→varies | `p=lambda g:[(A:=0)or[(A:=(C,max(B)^5^A)[A>0])for C in B]for B in g]` |
| **132** | 14.7 | same-shape | varies→varies | `def p(a): 	A=len(a[0]);D=sum(a,[]);E=D.index 	for B in{*D}-{0}: 		C=E(B);F=E(B,C+1);G,H=sorted((C%A,F%A)) 		for I in a[C//A:1+F//A]:I[G:-~H]=[B]*(H+1-G) 	return a` |
| **271** | 14.7 | shape-changes | (9, 9)→(3, 3) | `p=lambda g:max((str(B:=[B[A%7:][:3]for B in g[A//7:][:3]]).count('1'),B)for A in range(49))[1]` |
| **109** | 14.8 | shape-changes | varies→varies | `def p(g):A=len(g)>>1;return[B*0!=0and p(B)or(B>0)*g[A]for B in g[:A]+g[A-1::-1]]` |
| **300** | 14.8 | shape-changes | varies→varies | `p=lambda g,k=3:-k*g or[A for A in zip(*p(g,k-1))if max(range(1,10),key=sum(g,[]).count)in A]` |
| **091** | 14.8 | shape-changes | varies→varies | `p=lambda g,k=87:-k*g or p([*zip(*g[1-(5in g[k&1]):])][::-1],k-1)` |
| **343** | 14.8 | same-shape | (5, 15)→(5, 15) | `p=lambda g:[(r[:6+2*(r[:4]in(r[4:8],r[8:12]))]*3)[:15]for r in g]` |
| **279** | 14.8 | same-shape | varies→varies | `p=lambda g,k=56:k and p([[(A:=(k<29)*(B<2and A&8)or B%9or A&4or B)+(A==4)*(k<2)*5for B in(4,)+B][:0:-1]for B in zip(*g)],~-k)or g` |
| **365** | 14.8 | shape-changes | (10, 10)→varies | `p=lambda i,t=zip:i[(A:=(*map(any,i),0).index(0)):]and max(p(i[:A]),p(i[A+1:]),key=lambda z:str(z).count('2'))or t and[*t(*p([*t(*i)],0))]or i` |
| **055** | 14.8 | same-shape | varies→varies | `p=lambda a,m=1602080,h=0:a and[[max(A,m>>(h:=h+A)&7)for A in a.pop(0)]]+p(a,m>>3*(h>16))` |
| **062** | 14.8 | same-shape | (10, 10)→(10, 10) | `def p(g): 	for _ in' '*4: 		for(a,c)in enumerate((g:=[*zip(*g[::-1])])): 			for g[a]in({*c}=={0,2})*[*filter(sum,g[-~a:])]:a-=1 	return eval(f"{g}".replace(*'03'))` |
| **013** | 14.8 | same-shape | varies→varies | `p=lambda g:g[0][12:]and[*zip(*p([*zip(*g)]))]or exec('a,b=map(g.index,f:=[*filter(sum,g)]);g[a::b-a]=[[sum(r)]*len(r)for r in f*8][:len(g[a::b-a])]')or g` |
| **310** | 14.8 | shape-changes | varies→varies | `p=lambda g,a=0:a and[A for A in zip(*g)if min(a,key=a.count)in A]or p(p(g,(a:=sum(g,[]))),a)` |
| **281** | 14.9 | same-shape | varies→varies | `p=lambda g:exec('try:*_,b,d=[i for i,r in enumerate(g)if any(r)];D=d-b;1/(D>1);g[b:d+1]=[g[b-1]]*D+[g[b]]\nexcept:0\ng[:]=map(list,zip(*g[::-1]))\n'*4)or g` |
| **270** | 14.9 | same-shape | (15, 15)→(15, 15) | `def p(g,i=0,h={}): 	A,B=i//15,i%15;C=g[A][B];h[C]=A,B;i<224and p(g,i+1) 	if C>2:D,E=h[8%C];g[D+(A>D)-(A<D)][E+(B>E)-(B<E)],g[A][B]=C,0 	return g` |
| **228** | 14.9 | same-shape | (10, 10)→(10, 10) | `def p(g): 	B=sum(g,[]);C=sorted(B,key=B.count) 	for A in(0,1,2,3):D,E=divmod(B.index(C[A]),10);g[D+A//2*4-2][E+A%2*4-2],g[D][E]=C[3-A],0 	return g` |
| **289** | 14.9 | shape-changes | (3, 3)→varies | `p=lambda g:sum(([sum(zip(*[B]*(A:=len({*str(g)})-5)),())]*A for B in g),[])` |
| **183** | 14.9 | shape-changes | varies→varies | `def p(j):A=len(j)-2;C=range(2,A);return[[j[B][C]%7*j[-(B+B>A)][-(C+C>A)]for C in C]for B in C]` |
| **086** | 14.9 | same-shape | varies→varies | `# (decompressed) def p(a):  f=range  for d,e,r in[(d,e,3+(a[d][e+3]>0))for d in f(9)for e in f(9)if a[d][e]>a[~-d][e]\|a[d][~-e]<1]:   for u,p in(a[d][e],f(2-r,r*2-2)),(a[d+1][e+...` |
| **251** | 14.9 | same-shape | varies→varies | `p=lambda a,k=75:a*-k or p([[(v:=x or v&4,~-~x%3)[k<1]for x in(4,)+r][:0:-1]for r in zip(*a)],k-1)` |
| **390** | 14.9 | same-shape | (15, 15)→(15, 15) | `p=lambda g,k=1,r=range(15):-k*g or p([*zip(*(g[A-2*sum(A-B for B in r if g[B].count(2)>4>abs(A-B)>1)]for A in r))],k-1)` |
| **189** | 14.9 | shape-changes | (9, 9)→(6, 6) | `p=lambda i,R=range(6):[[i[A+3*(C:=i[2][4]>7)][B+3*(D:=i[4][2]>7)]%2*i[A//3-7*C-2][B//3-7*D-2]for B in R]for A in R]` |
| **240** | 14.9 | same-shape | (19, 19)→(19, 19) | `def p(g,R=range(19)): 	for B in R: 		for A in R:C,D=g[B],g[~B];C[A]\|=C[~A]\|D[A]\|D[~A] 		for A in R[B+2:~B:2]:g[A][B]=C[A]=C[B+2] 	return g` |
| **333** | 14.9 | same-shape | (10, 10)→(10, 10) | `p=lambda g:exec('g[:]=map(list,zip(*g[::-1]))\nfor r in g:\n for i in range(1,bytes(r).find(3)):r[i]\|=r[i-1]\n'*4)or g` |
| **163** | 14.9 | same-shape | (11, 11)→(11, 11) | `def p(g,R=range(11)):C,D=divmod(sum(g,[]).index(4),11);return[[5*(g[A][B]==5)or(A^C%4*4\|B^D%4*4<4)*g[C&-4\|A&3][D&-4\|B&3]for B in R]for A in R]` |
| **293** | 14.9 | same-shape | varies→varies | `p=lambda a:[[B^C^A[0]or B for(B,C)in zip(A,a[0])]for A in a]` |
| **376** | 14.9 | shape-changes | varies→varies | `p=lambda j:(j+j[1:-1])*2+j[:1]` |
| **008** | 14.9 | same-shape | varies→varies | `p=lambda g:exec('d=[*map(max,g)].index(8);g[:]=zip(*(sorted(g[:d],key=any)+g[d:])[::-1]);'*4)or g` |
| **156** | 14.9 | same-shape | (10, 10)→(10, 10) | `def p(a): 	C=E=0;D,A,*G=a 	for F in G: 		C\|=A<D 		for B in range(9): 			if A[B-1]*A[B+1]*D[B]*F[B]:A[B]=C+1;E+=1\|-C 		D,A=A,F 	return[[A^3*(E>0<A<3)for A in A]for A in a]` |
| **287** | 15.0 | same-shape | (16, 16)→(16, 16) | `p=lambda g:[[A[A[0]==4]for A in zip(A,B[::-1])]for(A,B)in zip(g,g[::-1])]` |
| **051** | 15.0 | same-shape | varies→varies | `p=lambda g,k=3:-k*g or p([[*r][:(i:=next((i+1for i in range(len(r)-2)if r[i]==0<r[i+1]!=r[i+2]>0),99))]+[x or r[i]for x in r[i:]]for r in zip(*g[::-1])],~-k)` |
| **148** | 15.0 | same-shape | varies→varies | `def p(g): 	A=g[4][0]-1 	for B,D in zip(*[[A for A in g if A[B]]for B in(0,-1)][::A]): 		if 8in B:C=B[::A];E=C.index(8);C[1:-~E]=[8]*~-E+[4];B[::A]=C;D[::A]=[8]*~-len(D)+[2] 	ret...` |
| **074** | 15.0 | same-shape | (30, 30)→(30, 30) | `p=lambda g:(A:=[[*map(min,(B:=[*map(min,*A)]),[9,9]+B[::-1])]for A in zip(g,zip(*g))])*(A==g)or p(A)` |
| **308** | 15.0 | shape-changes | varies→varies | `def p(g):s='for C,A in enumerate(sum(g,[])):\n ';B=len(g[0]);E=[0]*10;exec(s+'E[A]+=C');G=E.index(max(E));F=~-B//5;I=F-~F;J=[[G]*I for _ in[0]*I];exec(s+'if A-G:P=E[A]//4;J[C//B...` |
| **166** | 15.0 | same-shape | varies→varies | `p=lambda g:[[B[0]or 2*any(A)*any(B)for B in zip(A,*g)]for A in g]` |
| **206** | 15.0 | same-shape | varies→varies | `def p(g,f=filter,z=zip): 	B,A=divmod(sum(g,[]).index(5),len(g[0]));g[B][A]=0 	for(C,D)in z(g[B-1:],z(*f(sum,z(*f(sum,g))))):C[A-1:A+2]=D 	return g` |
| **079** | 15.0 | shape-changes | (14, 14)→(3, 3) | `p=lambda g:max((B:=[A for B in range(144)if all(map(sum,(A:=[A[B%12:][:3]for A in g[B//12:][:3]])+[*zip(*A)]))]),key=B.count)` |
| **184** | 15.0 | shape-changes | varies→varies | `from itertools import* p=lambda g,h=lambda g:zip(*[map(max,*b)for(k,b)in groupby(g,any)if k]):[*h(h(g))]` |
| **153** | 15.1 | shape-changes | (10, 10)→(3, 3) | `def p(g):B=sum(g,[]);*C,={*B}-{0};A,D=(sum((B[C]==A)<<C>>B.index(A)for C in range(100))for A in C);A^=7347207;E=0,1,2;return[[C[(A,D)[A!=(A&-A)*D]>>E+B*10&1]for E in E]for B in E]` |
| **059** | 15.1 | same-shape | (11, 11)→(11, 11) | `def p(g,r=range(11)): 	A=[0]*11 	for B in r: 		for C in r: 			if(D:=g[B][C])%5:A[B&12\|C>>2]+=1;E=D 	return[[[5,E*(A[B&12\|C>>2]==max(A))][B&3<3>C&3]for C in r]for B in r]` |
| **168** | 15.1 | same-shape | (10, 10)→(10, 10) | `p=lambda g:[exec('while 0<i<9>j>0:g[i:=i+a][j:=j+b]=k')for n in range(256)if(k:=g[(i:=1+n//32)][(j:=1+n//4%8)-(b:=n%-2\|1)])*g[i-(a:=(n&2)-1)][j]*g[i-a][j-b]]and g` |
| **397** | 15.1 | same-shape | (10, 10)→(10, 10) | `def p(g,b=80): 	B,A=b//9,b%9;C=g[B][A:A+2]+g[B+1][A:A+2] 	for D in g[B+2:][:len({*C})*all(C)]:D[A:A+2]=3,3 	if b:p(g,b-1);return g` |
| **242** | 15.1 | shape-changes | (16, 16)→(3, 3) | `p=lambda g:[A[~A.index(0)::-1][:3]for A in g if 0in A]` |
| **350** | 15.1 | same-shape | varies→varies | `p=lambda g:exec('g[:]=[[c or(1in r[:i])*(1in r[i:])*8for i,c in enumerate(r)]for r in zip(*g)];'*2)or g` |
| **084** | 15.1 | same-shape | varies→varies | `def p(j,i=1):  while j[i:]:j[-1][i]=4;j[~i][i]=2;i+=1  return j` |
| **143** | 15.1 | same-shape | (10, 10)→(10, 10) | `def p(g): 	i=sum(g,[]);d={} 	for c in i: 		if d.setdefault(sum(q-i.index(c)for q in range(100)if i[q]==c),c)-c:return eval(str(g).replace(str(c),'5'))` |
| **061** | 15.2 | same-shape | (18, 18)→(18, 18) | `p=lambda g,r=range(18):[[1+A*B%max(g[-1])for B in r]for A in r]` |
| **268** | 15.2 | same-shape | varies→varies | `def p(g):B=range(len(g));(C,D),*A,(F,E)=[(A,C)for A in B for C in B if g[A][C]];return g[C][D+2]and[*zip(*p([*zip(*g[::-1])]))][::-1]or[[g[A][B]\|4*((A<F)*(B-D>(A<=C)<E-B)\|(A<C)*...` |
| **169** | 15.2 | same-shape | (10, 10)→(10, 10) | `p=lambda g,k=15,m=1:-k*g or p([[((B:=A and(A\|B,m:=m*2)[k>14]),-A.bit_count()%5)[k<1]for A in(0,)+A][:0:-1]for A in zip(*g)],k-1)` |
| **031** | 15.2 | shape-changes | varies→varies | `p=lambda j:[*eval('zip(*filter(any,'*2+'j))))')]` |
| **022** | 15.2 | shape-changes | (11, 11)→(3, 3) | `p=lambda g,R=(-1,0,1):[[max(B[A+11*C+D]for A in range(121)if(B:=sum(g,[]))[A]==5)for D in R]for C in R]` |
| **075** | 15.2 | same-shape | (9, 13)→(9, 13) | `p=lambda g,r=range(9):[g[A][:4]+[g[A-A%3-8][B-B%3-8]*g[A%3][B%3]for B in r]for A in r]` |
| **256** | 15.2 | same-shape | varies→varies | `def p(j):C=max(j);B=sum(C)//2;A=D=j.index(C)+B;exec('j[D-A][:A]=[2+(A>B)-(A<B)]*A;A-=1;'*D);return j` |
| **217** | 15.2 | same-shape | (9, 9)→(9, 9) | `p=lambda g,r=range(9),m=max:[[m(m(g[A//3::3])[B//3::3])&m(m(g[A%3::3])[B%3::3])for B in r]for A in r]` |
| **330** | 15.2 | same-shape | (10, 10)→(10, 10) | `p=lambda g,k=63,m=2:-k*g or p([[A and((B\|A,(m:=m*2))[A&1],-~(A.bit_count()==6))[k<1]for(B,A)in zip((0,)+A,A)]for A in zip(*g[::-1])],k-1)` |
| **117** | 15.2 | same-shape | varies→varies | `# (decompressed) p=lambda h,r=range:(c:=len(h))and[[[max(h[a][m]for a in(a,2*i-a)for m in(e,2*f-e)if-1<a<c>m>-1)for e in r(c)]for a in r(c)]for i in r(1,c-1)for f in r(1,c-1)if ...` |
| **354** | 15.3 | same-shape | (10, 10)→(10, 10) | `def p(g): 	for B in g: 		while 5in B:D=(*B,0).index;A=D(5);C=D(0,A);B[A:C]=[max(g[0][A:C])]*(C-A) 	return g` |
| **218** | 15.3 | shape-changes | (21, 21)→varies | `p=lambda a,k=1:-k*[*a]or p({a:0for a in zip(*a)if max(a)},k-1)` |
| **197** | 15.3 | same-shape | varies→varies | `p=lambda g:[[*map({}.setdefault,g[1],A)]for A in g]` |
| **199** | 15.3 | same-shape | varies→varies | `p=lambda j:[((0,4)*8)[(A:=max(j))>A[1::2]:][:len(A)]]*-~(B:=j.index(A))+j[B:-1]` |
| **058** | 15.3 | same-shape | varies→varies | `p=lambda g:exec('C=A=0;B=len(g);E,D=-1,1\nwhile B>0:exec("g[C:=C+A][E:=E+D]=3;"*B);D,A=-A,D;B-=C<1or 2*A*A')or g` |
| **361** | 15.4 | same-shape | (10, 10)→(10, 10) | `p=lambda i,R=range:next(i for e in[3,2]for a in R(8)for b in R(8)if min(min(r[b:b+e])for r in i[a:a+e])and[exec(f"n,x={a+b+e-1}-x,{b-a}+n;i[n][x]=c;"*3)for n in R(10)for x in R(...` |
| **093** | 15.4 | same-shape | (14, 14)→(14, 14) | `p=lambda g,s=sorted:5in g[0]and[[5*(A>0)for A in s(A[:7])+s(A[7:])[::-1]]for A in g]or[*zip(*p([*zip(*g)]))]` |
| **035** | 15.4 | same-shape | (10, 10)→(10, 10) | `p=lambda g:exec('g[:]=map(list,zip(*g[::-1]))\nfor r in g:r[r[0]and r.index(8)]=r[0]\n'*4)or g` |
| **341** | 15.4 | same-shape | (10, 10)→(10, 10) | `def p(g):  for _ in'  ':   for r in[r for r in g if len({*r})>2][1:-1]:s={0};r[:]=[s.add(x)or x or~len(s)%2*8for x in r]   *g,=map(list,zip(*g))  return g` |
| **119** | 15.4 | same-shape | (12, 12)→(12, 12) | `def p(g): 	for e in(0,1)*4: 		c,*f=g=(g[::-1],[*map(list,zip(*g))])[e];a=0<(8in c)>sum(c[:(b:=c.index(8))]) 		for d in f*a:a-=d[b+a]&2;b+=a;d[b]=d[b]or 3 	return g` |
| **301** | 15.4 | same-shape | varies→varies | `p=lambda g,s=sorted:s(map(s,g))` |
| **298** | 15.4 | same-shape | varies→varies | `p=lambda g:[[g[2][~-A.index(B)%3]for B in A]for A in g]` |
| **303** | 15.4 | same-shape | varies→varies | `p=lambda a:[[C+2-2*any(B)*any(A)for(*B,C)in zip(*a,A)]for A in a]` |
| **237** | 15.4 | same-shape | varies→varies | `p=lambda g,t=0:[(A:=0)or[(A:=A or(t:=B))for B in B+[t]]for(*B,C)in g]` |
| **195** | 15.4 | shape-changes | varies→(9, 9) | `def p(I,f=filter,r=range(9)):*A,=f(any,zip(*f(any,I)));return[[A[C][B]&A[C*3%9][B*3%9]for C in r]for B in r]` |
| **178** | 15.5 | shape-changes | varies→varies | `p=lambda g:g*-1and g or[g for A in g if g!=(g:=p(A))]` |
| **019** | 15.5 | shape-changes | varies→varies | `def p(g): 	g=[r*2for r in g*2] 	for a,b in[*zip(g,g[1:]),*zip(g[1:],g)]:b[:]=map(lambda x,y,z:x or(y\|z)&7and 8,b,a[1:]+[0],[0]+a) 	return g` |
| **125** | 15.5 | same-shape | (15, 15)→(15, 15) | `def p(g,r=224):A,B=r//15,r%15;C=1,0,14;D=sum(g[A-D][B-E]&4for D in C for E in C);g[A][B]-=g[A][B]//8*D and(D<16)+4;r and p(g,r-1);return g` |
| **246** | 15.5 | same-shape | varies→varies | `def p(g): 	D=sum(g,[]).index;A=len(g[0]);B,C=D(2),D(3) 	while(B:=B+((C%A>B%A)-(C%A<B%A)or(A,-A)[B>C]))^C:g[B//A][B%A]=8 	return g` |
| **371** | 15.5 | same-shape | varies→varies | `def p(a): 	B=sum(a,[]).index;A=len(a[0]) 	for C in(0,1,-1,A,-A):C+=B(1)+B(1,-~B(1))>>1;a[C//A][C%A]=3 	return a` |
| **375** | 15.5 | same-shape | varies→varies | `def p(j,i=0):  for r in j:r[i]=r[~i]=0;i+=1  return j` |
| **374** | 15.5 | same-shape | (10, 10)→(10, 10) | `p=lambda g,i=19,c='1425':i>3and p(zip(*[(c:=c[(A:=(B:=str(C)[1::3]).replace(i//2*'5',i//2*c[0]))<B:])and map(int,A)for C in g]),i-1,c)or[*g]` |
| **277** | 15.5 | same-shape | (10, 10)→(10, 10) | `p=lambda i:(c:=[(b:=lambda y,x,k=k:10>y>-1<x<10>i[y][x]>7and(i[y].__setitem__(x,k)or-~sum(b(y+a//3-1,x+a%3-1)for a in range(9))))(*divmod(sum(i,[]).index(8),10))for k in(3,2,1)]...` |
| **012** | 15.6 | same-shape | (12, 12)→(12, 12) | `p=lambda g:(B:=sum(g,[]),[g[(A+D)//12].__setitem__((A+D)%12,B[A-(C%23<3)])for A in range(144)if 3>B.count(B[A])for C in(2,11,13,22,24,26)for D in(C,-C)])and g` |
| **068** | 15.6 | same-shape | (10, 10)→(10, 10) | `p=lambda g:[*zip(*[((C==(B:=(A:=sum(g,[])).index(min(A,key=A.count))))*A[B]\|2&7172>>abs(C-B)for C in range(100))]*10)]` |
| **134** | 15.6 | shape-changes | varies→(3, 3) | `def p(g):D,A=sorted({*sum(g,[])}-{0},key=lambda c:str(g).count(f"{c}, {c}"));B=[B for B in g if A in B];C=len(B)//3;return[[D*(B==A)for B in E[min(B.index(A)for B in B)::C][:3]]...` |
| **260** | 15.6 | same-shape | (10, 10)→(10, 10) | `def p(g,A=range(10)):B={C-B:F^5for B in A for C in A if(F:=g[B][C])};C=max(B,key=B.get);D,*G,E=sorted(B);return[[A-F in{C,D-2*(D<C),E+2*(E>C)}and 5^B[C]for A in A]for F in A]` |
| **295** | 15.6 | shape-changes | varies→varies | `def p(g):A,=g;return g+[(A:=A[:1]+A[:-1])for B in A[3::2]]` |
| **250** | 15.6 | same-shape | (10, 10)→(10, 10) | `p=lambda i,k=3:-k*i or p([[0]*~-(A:=8-str(i).find('2')//33)+[max(B[:A]),*B[A:]]for B in zip(*i[::-1])],k-1)` |
| **362** | 15.6 | same-shape | (10, 10)→(10, 10) | `def p(g):A=g.count(g[0]);B=max(g);C=[g[9][A:]+[0]*A]*10;C[A+g.index(B)]=B;return C` |
| **355** | 15.6 | shape-changes | varies→(1, 1) | `p=lambda g:[[sorted(range(10),key=lambda k:sum(A.count(k)-(k in A)*sum(k in A for A in zip(*g))for A in g))[1]]]` |
| **041** | 15.6 | same-shape | (10, 10)→(10, 10) | `p=lambda j,a=0:[[A\|(a:=a^A)for A in A]for A in j]` |
| **345** | 15.6 | same-shape | (10, 10)→(10, 10) | `def p(j): 	for A in range(9): 		for B in((C:=j[9])[A]>1)*j[::-1]:A+=B[A]>4;C[A]=B[A]=2;C=B 	return j` |
| **342** | 15.6 | same-shape | (10, 10)→(10, 10) | `def p(g): 	C=sum(g,[]);A=C.index(8);g=[10*[0]for A in g];B=0 	for D in C:g[A//10+(B>A)][A%10+(B%10>A%10)]\|=D*(D!=8);B+=1 	return g` |
| **034** | 15.7 | same-shape | (9, 9)→(9, 9) | `def p(g): 	A=sum(g,[]);B=[(B//9,B%9)for B in range(81)if A[B]];G,H=B[0] 	for(E,F)in B: 		for(C,D)in B*(A[E*9+F]==2): 			while-1<C<9>D>-1:g[C][D]=sum({*A})-2;C-=G-E\|1;D-=H-F\|1 	r...` |
| **102** | 15.7 | same-shape | (12, 12)→(12, 12) | `def p(g,d=1536): 	while d: 		d-=1;A,B=d&7,d>>7;C=A+2;D=g[d>>3&15:][:C];E=[C*[5]] 		for F in([A[B:B+C]for A in D]==E+A*[[5,*[0]*A,5]]+E)*D[1:-1]:F[B+1:B-~A]=A*[2] 	return g` |
| **190** | 15.7 | same-shape | (10, 10)→(10, 10) | `p=lambda g:[exec('while-1<i<10>j>-1:g[i][j]=k;i+=a;j+=b')for n in range(256)if(k:=g[i:=n>>5][j:=n>>2&7])*g[i-(a:=(n&2)-1)][j]*g[i+a][j+(b:=n%-2\|1)]]and g` |
| **225** | 15.7 | same-shape | (6, 6)→(6, 6) | `p=lambda g,R=range(6):[[[g[C][D]+g[A+(C<A)][B+(D<B)]*(C-A&D-B&2>0)for D in R]for C in R]for A in R for B in R if g[A][B]][0]` |
| **124** | 15.7 | shape-changes | varies→(10, 10) | `p=lambda a,k=6:(A:=[(A//(B:=k//3)*(k%3)*[0]+a[A%B])[:10]for A in range(10)])*(A[:5]==a[:5])or p(a,-~k)` |
| **304** | 15.7 | shape-changes | (3, 3)→(9, 9) | `p=lambda j:[[k*(K==max(s:=sum(j,[]),key=s.count))for K in I for k in i]for I in j for i in j]` |
| **188** | 15.7 | shape-changes | varies→varies | `p=lambda g:g[3:]and(A:=g[:len(g)>>1])*2==g and A or[*zip(*p([*zip(*g)]))]` |
| **329** | 15.8 | same-shape | varies→varies | `p=lambda a:[(m:=len(r)//2)*[0]+[r[m]]+m*[0]for r in a]` |
| **094** | 15.8 | same-shape | (15, 15)→(15, 15) | `p=lambda g,k=1:-k*g or p([[B[A]-B[A]//8*2*([1]*5in[B[A-2:A+3]for B in g])for B in g]for A in range(15)],k-1)` |
| **391** | 15.8 | shape-changes | varies→(3, 1) | `p=lambda a:[*zip(sorted({*(A:=sum(a,[]))},key=A.count)[2::-1])]` |
| **312** | 15.8 | same-shape | (12, 12)→(12, 12) | `p=lambda g:[[(B>0)*A[0]for B in A]for A in g]` |
| **082** | 15.8 | same-shape | varies→varies | `p=lambda j:[A:=j[0],[*map(max,A[1:]+[0],[0]+A)]]*3` |
| **297** | 15.9 | same-shape | varies→varies | `p=lambda j:j[:2]+[*zip(*j[:1]*len(j[0]))]*2` |
| **346** | 15.9 | shape-changes | varies→(1, 1) | `p=lambda g:[[min(sum(g,[]),key=lambda c:f"{g,*zip(*g)}".count(f"{c}, {c}"))]]` |
| **024** | 15.9 | same-shape | varies→varies | `p=lambda g:[[sum({*A}&{1,3}or{*B}&{2})for B in zip(*g)]for A in g]` |
| **050** | 15.9 | same-shape | varies→varies | `p=lambda g,k=1:-k*g or p([[C\|3*(8in A[:B])*(8in A[-~B:])for(B,C)in enumerate(A)]for A in zip(*g)],k-1)` |
| **290** | 15.9 | shape-changes | varies→varies | `p=lambda a,s=sum:[[s({*s(a,[])})-A for A in A if A]for A in a if s(A)]` |
| **049** | 15.9 | shape-changes | varies→varies | `p=lambda g:[[A]*B.count(A)for B in g if(A:=min({*(C:=sum(g,[]))}-{0},key=C.count))in B]` |
| **269** | 15.9 | shape-changes | (3, 3)→varies | `p=lambda g:sum(([sum(zip(*[B]*(A:=len({*str(g)})-5)),())]*A for B in g),[])` |
| **360** | 16.0 | shape-changes | (10, 9)→(10, 4) | `p=lambda g:[[*map(max,r,r[:4:-1])]for r in g]` |
| **239** | 16.0 | shape-changes | varies→varies | `def p(a):s=sum(a,[]);c=s.count;a=sorted({*s},key=c)[::-1];return[[v*(i<c(v))for v in a]for i in range(c(a[0]))]` |
| **245** | 16.0 | same-shape | varies→varies | `def p(g): 	A=len(g[0]);B=sum(g,[]);C=[(B//A,B%A)for(B,C)in enumerate(B)if C%3];G,H=map(min,*C);D=~B.index(3) 	for(E,F)in C:g[E][F]^=2;g[E-G-D//A][F-H-D%A]^=2 	return g` |
| **212** | 16.0 | same-shape | (10, 10)→(10, 10) | `def p(g,a=99): 	A=a//10;C=g.index(max(g));B=g[A][a%10] 	for D in g[A:(A,None,C)[B%3]:B&1^(A<C)or-1]:D[a%10]=B 	if a:p(g,a-1);return g` |
| **021** | 16.0 | shape-changes | varies→varies | `p=lambda g,f=lambda _:-~min(map(_.count,_)):[g[0][:1]*f(g[0])]*f(g)` |
| **042** | 16.0 | same-shape | (10, 10)→(10, 10) | `def p(g):B=range(9);D={(A,C,g[A][C:].index(0))for A in B for C in B if g[A-1][C]^3};[g[E].__setitem__(J,8)for(F,G,A)in D for C in(-A,A)if(F+A,G+C,A)in D for H in(-1,2)for I in B...` |
| **057** | 16.0 | shape-changes | (8, 8)→(3, 6) | `p=lambda a:eval('[*filter(sum,zip(*'*2+'a))]*2))]')` |
| **254** | 16.0 | same-shape | (9, 9)→(9, 9) | `p=lambda g,z=zip:[[B%2*(A==max(z(*g)),2)[A==sorted({*z(*g)})[1]]for(A,B)in z(z(*g),A)]for A in g]` |
| **176** | 16.0 | same-shape | varies→varies | `p=lambda g:[[C\|A>>B%12&4for(B,C)in enumerate(B)]for(A,B)in zip((896,260,8204),g)]` |
| **372** | 16.0 | shape-changes | (11, 11)→(5, 11) | `p=lambda g:[[*map(max,*a)]for a in zip(g,g[6:])]` |
| **040** | 16.0 | same-shape | (10, 10)→(10, 10) | `p=lambda j,r=range(10):[[j[A][B]and j[A//5*9][B//5*9]for B in r]for A in r]` |
| **332** | 16.0 | same-shape | varies→varies | `p=lambda g:[[x-j%2*x%3for j,x in enumerate(r,len(r))]for r in g]` |
| **302** | 16.0 | same-shape | (12, 12)→(12, 12) | `p=lambda a:[exec('B[A]=C+(C<6)*B[A:].index(5)')for(B,D)in zip(a[1:],a)for(A,E)in enumerate(B)if E<1<A*D[A]*(C:=B[A-1])]and a` |
| **039** | 16.0 | shape-changes | (10, 10)→(3, 3) | `p=lambda g:[*eval('zip(*[*filter(any,'*2+'g)]))][:3])')][:3]` |
| **141** | 16.0 | same-shape | varies→varies | `def p(g):A=range(len(g));return[[sum(g[D][B]*(E-D in(C-B,B-C))for D in A for B in A)for C in A]for E in A]` |
| **327** | 16.1 | shape-changes | (3, 3)→(6, 6) | `p=lambda g,l=[0]*3:[l:=[*map(max,[0]+l*2,r+[0]*3)]for r in g+[l]*3]` |
| **180** | 16.1 | shape-changes | (8, 8)→(4, 4) | `p=lambda j:[[max(A,key=bool)for A in zip(A[4:],B,B[4:],A)]for(A,B)in zip(j,j[4:])]` |
| **045** | 16.1 | same-shape | (10, 10)→(10, 10) | `p=lambda g:[10*A[:A[9]==A[0]]or A for A in g]` |
| **369** | 16.1 | same-shape | (10, 10)→(10, 10) | `p=lambda g,k=63,m=1:-k*g or p([[((v:=A and A\|v,(A<1)*-~(m:=m*2))[k>62],5-A.bit_count())[k<1]for A in(0,)+A][:0:-1]for A in zip(*g)],k-1)` |
| **007** | 16.1 | same-shape | (7, 7)→(7, 7) | `p=lambda g,k=2:[[max(sum(g,[])[(k:=-~k)%3::3])for _ in r]for r in g]` |
| **263** | 16.1 | shape-changes | varies→(3, 3) | `p=lambda g:g[3:]and(A:=sorted((str(A).count('0'),A)for A in zip(*[iter(g)]*3)))[-(A[0]>A[1][:1])][1]or[*zip(*p([*zip(*g)]))]` |
| **348** | 16.1 | same-shape | varies→varies | `p=lambda g,e=enumerate:[[(A<B<-A)*(7+B%2)for(B,C)in e(B,-g[0].index(7))]for(A,B)in e(g,-g.count(g[0]))]` |
| **105** | 16.1 | same-shape | varies→varies | `def p(g):E=*zip(*g),;e=enumerate;b,*_,c=[a for a,b in e(g)if 1in b];d=bytes(map(any,E)).rfind(1);return[[v or 2*(b<=y<=c>1<x<=d)*(y in(b,c)or x%d<3or sum(r[3:d]+[*E[x][b+1:c]])>...` |
| **259** | 16.2 | shape-changes | varies→varies | `p=lambda g,k=19:eval(f"{-k*g or p([*zip(*g[2>max(g[0]):][::-1])],~-k)}".replace(*'10'))` |
| **043** | 16.2 | same-shape | (10, 10)→(10, 10) | `p=lambda j:[[B\|2&C+A[9]for(B,C)in zip(A,j[0])]for A in j]` |
| **357** | 16.2 | same-shape | varies→varies | `def p(g,t=9): 	for A in g:B=~-len(A);A[:]=[8]*-~B;A[~abs(t%(2*B)-B)]=1;t-=1 	return g` |
| **100** | 16.2 | shape-changes | (10, 10)→(2, 2) | `p=lambda g:[[max(range(1,10),key=lambda x:max((A:=[A.count(x)for A in g]))*(A.count(2)+2))]*2]*2` |
| **121** | 16.2 | shape-changes | (13, 13)→(3, 3) | `def p(a):a=sum(a,[]);a=a[a.index(8)-14:];return[a[:3],[a[13],max(a[:3]),a[15]],a[26:29]]` |
| **248** | 16.2 | same-shape | varies→varies | `def p(g,t=9): 	for B in g:A=~-len(B);B[~abs(t%(A+A)-A)]=1;t-=1 	return g` |
| **388** | 16.2 | shape-changes | varies→varies | `p=lambda g:[[t[0]or 8*any(t)for t in zip(r,*g)]*2for r in g*2]` |
| **292** | 16.3 | same-shape | varies→varies | `p=lambda g:[[A\|A>>B for(A,B)in zip(A,(1,0,0)*9)]for A in g]` |
| **247** | 16.3 | shape-changes | (10, 10)→varies | `def p(a):a=sum(zip(*a),());A=a.count;B=max(map(A,{*a}-{0}));return[[*{C:0for C in a if A(C)==B}]]*B` |
| **030** | 16.3 | same-shape | varies→varies | `p=lambda g:[*zip(*(A[(B:=(C:=sum(g,[]).index)(max(A))//10-C(1)//10):]+A[:B]for A in zip(*g)))]` |
| **273** | 16.3 | same-shape | (10, 10)→(10, 10) | `def p(g): 	A=B=0 	for C in g: 		try:D=C.index;A=D(4)+1;B^=D(4,A)-A 		except:C[A:A+B]=[2]*B 	return g` |
| **027** | 16.3 | same-shape | (10, 10)→(10, 10) | `p=lambda a,R=range(10):[[a[A][B]or 2*a[B][(0<sum((a[B][-A]-a[B][~A])*a[A][B]for A in R for B in R))+~A]for B in R]for A in R]` |
| **060** | 16.4 | same-shape | (5, 11)→(5, 11) | `p=lambda g:[5*[A]+[5%6**A]+5*[B]for(A,*C,B)in g]` |
| **321** | 16.4 | shape-changes | (4, 14)→(4, 4) | `p=lambda j:[[A.pop(0)or A[4]\|A[9]for B in j]for A in j]` |
| **353** | 16.4 | same-shape | varies→varies | `def p(j):(A,B),(C,D)=[divmod(sum(j,[]).index(A),len(j[0]))for A in(3,4)];j[A][B]=0;j[A+(C>A)-(A>C)][B+(D>B)-(B>D)]=3;return j` |
| **048** | 16.4 | shape-changes | varies→(1, 1) | `def p(g): 	for d in g:d+=0,;c=len(d);b=sum(g,[])+[0]*c;e=[b.index(2)] 	for a in e:e+=b[a]*(a-1,a+1,a-c,a+c);b[a]=0 	return[[8-8*(2in b)]]` |
| **010** | 16.5 | same-shape | (9, 9)→(9, 9) | `p=lambda g,z=zip:[[A%4*sum(A>=B for A in z(*g))for(A,B)in z(A,z(*g))]for A in g]` |
| **356** | 16.5 | same-shape | (10, 10)→(10, 10) | `p=lambda g,e=enumerate,m=max:[[m(B[:C+1])&m(B[C:])\|m(D[:A+1])&m(D[A:])for(C,D)in e(zip(*g))]for(A,B)in e(g)]` |
| **028** | 16.5 | same-shape | (10, 10)→(10, 10) | `p=lambda g,b=range(10):[[(B*(A%7&5)%9<1)*max(g[2+A-A%5])for B in b]for A in b]` |
| **136** | 16.5 | same-shape | (10, 10)→(10, 10) | `def p(g): 	for A in(-1,1): 		B,C=divmod(sum(g,[]).index(A%3),10) 		while B<10>C>-1<B:g[B][C]=A%3;B-=A;C-=A 	return g` |
| **078** | 16.5 | same-shape | (10, 10)→(10, 10) | `p=lambda a:[*zip(*[sorted(x,key=0..__eq__)for x in zip(*a)])]` |
| **226** | 16.5 | same-shape | (10, 10)→(10, 10) | `def p(g): 	def A(x,y): 		if-1<x<10>y>=g[x][y]<1:g[x][y]=B;A(x-1,y),A(x+1,y),A(x,y-1),A(x,y+1) 	B=2;A(4\|g[4][0],4\|g[0][4]);B=1;A(0,0);B=3;A(9,9);return g` |
| **394** | 16.5 | shape-changes | varies→varies | `p=lambda g:[g[:(B:=2\|len(g)//7)+B][g.index(A)-B][A.index(0):][:C]for A in g if(C:=A.count(0))]` |
| **336** | 16.5 | same-shape | (10, 10)→(10, 10) | `def p(a,T=range(10)): 	(C,D),*G,(E,F)=[(A,B)for A in T for B in T if a[A][B]] 	for A in T[C:E+1]: 		for B in T[D:F+1]: 			while~A*~B%11>0==a[A][B]:a[A][B]=8;A+=(A>C)-(A<E);B+=(B...` |
| **323** | 16.6 | same-shape | (13, 13)→(13, 13) | `def p(g): 	for C in(-1,1): 		A,B=divmod(sum(g,[]).index(8),13);D=0 		while-1<((B:=B+C)if D&2else(A:=A-C))<13:g[A][B]=5;D+=1 	return g` |
| **160** | 16.6 | same-shape | (10, 10)→(10, 10) | `def p(g,k=63): 	B,D,C,*E=g[k>>3:];A=slice(k&7,k%8+3) 	if min(B[A]+C[A]):B[A]=C[A]=0,2,0;D[A]=2,2,2 	if k:p(g,k-1);return g` |
| **274** | 16.6 | shape-changes | varies→(3, 3) | `p=lambda a:[(a:=[8]*[*map(max,a)].count(5)+[0]*7)[1:4],a[6:3:-1],[0]*3]` |
| **291** | 16.6 | shape-changes | varies→(1, 1) | `import re p=lambda g:[[int(re.split('([^0]), (0, )+\\1',str(g))[1])]]` |
| **130** | 16.7 | shape-changes | (9, 9)→(3, 3) | `p=lambda g:[[max({*B[A:A+3]}-{5})for A in(0,3,6)]for B in g[::3]]` |
| **115** | 16.7 | shape-changes | varies→varies | `p=lambda g:(A:=[*{}.fromkeys(g[0])])[1:]and[A]or[*zip(*p([*zip(*g)]))]` |
| **296** | 16.7 | shape-changes | (5, 7)→(3, 3) | `p=lambda g:eval("[[a,b\|c,d]for(a,b,*e,c,d)in zip(*"*2+"g)])]")` |
| **123** | 16.7 | shape-changes | (5, 5)→(10, 10) | `p=lambda g:[[(B:=g[0][:4+all(g[0])]*3)[A]]*A+B[A:10]for A in range(10)]` |
| **305** | 16.7 | same-shape | (16, 16)→(16, 16) | `p=lambda g,r=range(16):[[1+(A+B)%max(g[0])for B in r]for A in r]` |
| **316** | 16.7 | shape-changes | (10, 10)→(3, 3) | `p=lambda j:[(a:=[*filter(int,map(max,*j))]+9*[0])[:3],a[5:2:-1],a[6:9]]` |
| **262** | 16.8 | same-shape | (3, 3)→(3, 3) | `p=lambda j:[[3+(b-a)/5]*3for a,b,_ in j]` |
| **104** | 16.8 | shape-changes | (3, 3)→(9, 9) | `p=lambda g,k=2,v=0:[k-1and p(g,1,A)or(v^A<4<8>A)*3for A in range(9)[::g[k][-k]%-2\|1]]` |
| **139** | 16.8 | same-shape | (9, 9)→(9, 9) | `p=lambda a:exec('for i in range(18):j=(x:=any(a[8])*2,5)[k:=i>8]+i%3;r=a[1+i//3+x*k];r[j]=r[j]or 7')or a` |
| **099** | 16.8 | same-shape | (10, 10)→(10, 10) | `def p(g): 	for A in(0,1,4): 		for(B,C)in zip(g,g[1:]):B[A:A+5]=[B or max([*zip(*g)][A+2])*C[A]*C[A+4]for B in B[A:A+5]] 	return g` |
| **381** | 16.8 | same-shape | (10, 10)→(10, 10) | `p=lambda g:g[:1]+[[A[B]or 9*any(A[:B])*any(A[B:])for B in range(10)]for A in g[1:9]]+g[9:]` |
| **032** | 16.9 | same-shape | varies→varies | `p=lambda g:[*zip(*map(sorted,zip(*g)))]` |
| **315** | 16.9 | shape-changes | (3, 3)→(9, 9) | `p=lambda j:[[x*(c>1)for c in R for x in r]for R in j for r in j]` |
| **200** | 16.9 | same-shape | (10, 10)→(10, 10) | `p=lambda g:[([0]*g[9].index((A:=sum(g[9])))+[A,0**B*5,A,B//9*5]*3)[:10]for B in range(10)]` |
| **047** | 17.0 | same-shape | (9, 9)→(9, 9) | `p=lambda g:[[sum({*A,*B})%13for B in zip(*g)]for A in g]` |
| **320** | 17.0 | same-shape | varies→varies | `p=lambda g:[*zip(*(A[:-(B:=sum(A)>>2)]+B*(8,)or A for A in zip(*g)))]` |
| **001** | 17.1 | shape-changes | (3, 3)→(9, 9) | `p=lambda g:[[X&x for X in A for x in a]for A in g for a in g]` |
| **122** | 17.2 | same-shape | varies→varies | `p=lambda g:7in map(sum,g)and[*zip(*p([*zip(*g)]))]or[[A%2*A\|B%3for(A,B)in zip(A,(0,0,*A))]for A in g]` |
| **081** | 17.3 | same-shape | (7, 7)→(7, 7) | `import re p=lambda a,k=3:a*-k or p([*zip(*eval(re.sub('0(?=, 8.{19}8, 8)','1',str(a)))[::-1])],k-1)` |
| **146** | 17.3 | shape-changes | (9, 3)→(3, 3) | `p=lambda g:(A:=g[:3])*(A!=[*map(list,zip(*A))])or p(g[3:])` |
| **038** | 17.3 | shape-changes | (9, 9)→(1, 5) | `p=lambda g:[([1]*str(g).count('1, 1')+[0]*9)[:9:2]]` |
| **207** | 17.5 | shape-changes | (5, 5)→(2, 2) | `p=lambda j:min((A:=[[j[B][A:A+2],j[B+1][A:A+2]]for B in[0,3]for A in[0,3]]),key=A.count)` |
| **083** | 17.5 | shape-changes | (3, 4)→(6, 8) | `p=lambda j:[r+r[::-1]for r in j+j[::-1]]` |
| **108** | 17.5 | shape-changes | (10, 10)→(20, 20) | `p=lambda g:g and[sum(zip(*[g[1][1::2]]*4),())]*4+p(g[2:])` |
| **299** | 17.6 | same-shape | (6, 6)→(6, 6) | `p=lambda g:[[(A,A%6+2)[2in B]for A in g[0]]for B in g]` |
| **142** | 17.7 | shape-changes | (3, 3)→(6, 6) | `p=lambda j:[r+r[::-1]for r in j+j[::-1]]` |
| **152** | 17.7 | shape-changes | (3, 3)→(6, 6) | `p=lambda j:[r+r[::-1]for r in j+j[::-1]]` |
| **194** | 17.7 | shape-changes | (3, 3)→(6, 6) | `p=lambda g:g+[A.__iadd__(B[::-1])[::-1]for(A,*B)in zip(g,*g)][::-1]` |
| **211** | 17.7 | shape-changes | (3, 2)→(9, 4) | `p=lambda j:[r[::-1]+r for r in j[::-1]+j+j[::-1]]` |
| **389** | 17.7 | same-shape | varies→varies | `p=lambda j:[[sum({*sum(j,A)}-{5,B})for B in A]for A in j]` |
| **229** | 17.7 | same-shape | (3, 3)→(3, 3) | `p=lambda j:[[(5,x)[x==max(f:=sum(j,[]),key=f.count)]for x in r]for r in j]` |
| **214** | 17.8 | same-shape | (3, 11)→(3, 11) | `p=lambda g:[A[:4]+(C[:4]+B)[::-1]for(A,*B,C)in zip(g,*g,g[::-1])]` |
| **072** | 17.8 | shape-changes | (13, 5)→(6, 5) | `p=lambda g:[[3*(x!=y)for x,y in r]for r in map(zip,g,g[7:])]` |
| **114** | 17.9 | shape-changes | varies→varies | `p=lambda g:[[0,*g[0],0],*(r[:1]+r+r[-1:]for r in g),[0,*g[-1],0]]` |
| **235** | 17.9 | shape-changes | (4, 14)→(3, 3) | `p=lambda g:[3*[(7*g[2][A-1]+5*g[2][A]+g[1][A])%9]for A in(1,6,11)]` |
| **052** | 17.9 | same-shape | (3, 3)→(3, 3) | `p=lambda j:[3*[len({*A})%2*5]for A in j]` |
| **267** | 17.9 | same-shape | (7, 7)→(7, 7) | `p=lambda j:[[j[6][A>[B]]for B in A]for A in j]` |
| **181** | 17.9 | same-shape | (6, 9)→(6, 9) | `def p(j): 	for A in j[:3]:B=j[3][5]%3*6;A[B:B+3]=A[5:2:-1] 	return j` |
| **003** | 17.9 | shape-changes | (6, 3)→(9, 3) | `p=lambda g:eval(str(g+g[g[0]==g[3]:][2:5]).replace(*'12'))` |
| **399** | 17.9 | shape-changes | varies→(3, 3) | `p=lambda g:[[1,0,(A:=sum(sum(g,[]))/8)>1],[0,A>2,0],[A>3,0,A>4]]` |
| **106** | 17.9 | shape-changes | varies→varies | `p=lambda g:g+[A.__iadd__(B)[::-1]for(A,*B)in zip(g,*g[::-1])][::-1]` |
| **227** | 18.0 | shape-changes | (8, 4)→(4, 4) | `p=lambda g:[[2*(A==B)for(A,B)in A]for A in map(zip,g,g[4:])]` |
| **257** | 18.0 | shape-changes | (9, 9)→(4, 4) | `p=lambda a:a[0][4:]and p([[B[A]or B[A-4]for B in a]for A in range(4)])or a` |
| **098** | 18.2 | same-shape | varies→varies | `p=lambda g,e=enumerate:[[C*any(0in A[B-1:B+2]for A in g[A-1:A+2])for(B,C)in e(B)]for(A,B)in e(g)]` |
| **120** | 18.2 | same-shape | varies→varies | `p=lambda g,e=enumerate:[[(C,8)[sum(sum(A[B-1:B+2])for A in g[A-1:A+2])>8*C>0]for(B,C)in e(B)]for(A,B)in e(g)]` |
| **147** | 18.2 | same-shape | varies→varies | `p=lambda g,k=3:-k*g or p([[(A,8)[A*B>2]for(B,A)in zip((0,)+A,A)]for A in zip(*g[::-1])],~-k)` |
| **151** | 18.2 | same-shape | varies→varies | `p=lambda j:exec('e,k=[s.index(max(s))for s in(j,j[0])]\nfor i in-1,1:j[e+i][k-1:k+2]=[4]*3;j[e][k+i]=4')or j` |
| **171** | 18.2 | same-shape | varies→varies | `p=lambda g:exec('g[:]=zip(*g[:0:-1],9*[8]);'*4)or g` |
| **266** | 18.2 | same-shape | (3, 5)→(3, 5) | `p=lambda g:[[{-6:3,-4:6,4:8,6:7}.get(5*C+A-(B:=sum(g,[]).index(2)),0)*(A-B%5&1)for A in range(5)]for C in(0,1,2)]` |
| **283** | 18.2 | same-shape | (10, 10)→(10, 10) | `p=lambda g,z=[[0]*10]:[[b'024100'[sum(A)%6]%8for A in zip(A,B,C,[0]+A,A[1:]+[0])]for(B,A,C)in zip(z+g,g,g[1:]+z)]` |
| **294** | 18.2 | same-shape | (10, 10)→(10, 10) | `import re p=lambda g:eval(re.sub('(?<=5.{31}5, )5(?=, 5.{31}5)','2',str(g)))` |
| **331** | 18.2 | same-shape | (10, 10)→(10, 10) | `p=lambda g:[(g:=[*zip(*eval(str(g).replace('1, 0','1,'+c))[::-1])])for c in'6278']and g` |
| **344** | 18.2 | same-shape | varies→varies | `p=lambda g,k=3:-k*g or p(eval(str([*zip(*g)][::-1]).replace('2, 3','0,8')),k-1)` |
| **352** | 18.2 | same-shape | varies→varies | `p=lambda a,e=enumerate:[[C or any(2in[0,*A][B:B+3]for A in[[],*a][A:A+3])for(B,C)in e(B)]for(A,B)in e(a)]` |
| **015** | 18.2 | same-shape | (9, 9)→(9, 9) | `p=lambda g:([exec('x,y=1,A-1;'+'g[i//9+x][i%9+y]=A^6;x,y=-y,x;'*4)for i in range(81)if 3>(A:=g[i//9][i%9])>0],g)[1]` |
| **095** | 18.2 | same-shape | (9, 9)→(9, 9) | `p=lambda g:eval("[[r[i]\|any((0,*r)[i:i+3])for i in range(9)]for r in zip(*"*2+"g)])]")` |
| **127** | 18.2 | same-shape | varies→varies | `p=lambda g,e=enumerate:[[5+(C<5)*g[A&4\|1][B&-4\|1]for(B,C)in e(B)]for(A,B)in e(g)]` |
| **220** | 18.2 | same-shape | varies→varies | `p=lambda g,e=enumerate:[[(sum(sum((0,*A)[B:B+3])for A in[[],*g][A:A+3])+C)*5%9for(B,C)in e(B)]for(A,B)in e(g)]` |
| **230** | 18.2 | same-shape | varies→varies | `def p(g): 	B,C,D,E,*F=g 	for A in range(16): 		if[5]*4==C[A:A+2]+D[A:A+2]:B[A-1:A+3:3]=1,2;E[A-1:A+3:3]=3,4 	if F:p(g[1:]);return g` |
| **282** | 18.2 | same-shape | (9, 9)→(9, 9) | `p=lambda g,R=range(9):[[sum(g[a][b]**((i-a)**2+(j-b)**2)//5%25for a in R for b in R)for j in R]for i in R]` |
| **317** | 18.2 | same-shape | (9, 9)→(9, 9) | `p=lambda g,r=b'111444777':[[4<g[A&7][B&7]for B in r]for A in r]` |
| **339** | 18.2 | shape-changes | (3, 3)→varies | `p=lambda j:[[*filter(int,sum(j,[]))]]` |
| **386** | 18.2 | shape-changes | (4, 7)→(4, 3) | `p=lambda j:[[3>>B+A.pop(4)for B in A[:3]]for A in j]` |
| **111** | 18.3 | shape-changes | (10, 10)→(3, 3) | `p=lambda g:[(A:=sum(g,[]))[A.index(5)+B:][:3]for B in(9,19,29)]` |
| **249** | 18.3 | shape-changes | varies→varies | `p=lambda j:[E*2for E in j]` |
| **318** | 18.4 | shape-changes | (9, 4)→(4, 4) | `p=lambda j:[[3*any(x)for x in r]for r in map(zip,j,j[5:])]` |
| **380** | 18.4 | same-shape | (3, 3)→(3, 3) | `p=lambda j:[*zip(*j)][::-1]` |
| **026** | 18.4 | shape-changes | (5, 7)→(5, 3) | `p=lambda j:[[8>>B+A.pop(4)for B in A[:3]]for A in j]` |
| **150** | 18.4 | same-shape | varies→varies | `p=lambda j:[r[::-1]for r in j]` |
| **155** | 18.4 | same-shape | varies→varies | `p=lambda j:j[::-1]` |
| **167** | 18.5 | same-shape | (3, 3)→(3, 3) | `r=0,1,2 p=lambda g:[[5*(B==(0,A,2-A)[len({*str(g)})%5])for A in r]for B in r]` |
| **395** | 18.5 | shape-changes | (6, 3)→(3, 3) | `p=lambda g:[[2-2*any(A)for A in zip(A,g.pop(3))]for A in g]` |
| **006** | 18.5 | shape-changes | (3, 7)→(3, 3) | `p=lambda j:[[a*r.pop(4)*2for a in r[:3]]for r in j]` |
| **347** | 18.5 | shape-changes | (3, 6)→(3, 3) | `p=lambda j:[[B\|A.pop(3)and 6for B in A]for A in j]` |
| **236** | 18.5 | shape-changes | (9, 4)→(4, 4) | `p=lambda a:[[3*(x^y>>1)for x,y in s]for s in map(zip,a,a[5:])]` |
| **334** | 18.6 | shape-changes | (5, 5)→(3, 3) | `p=lambda j,x=[0,5,0],y=[5]*3:[[[0,0,5]]*2+[y],[y,x,x],[x,y,x]][-max(max(j))]` |
| **373** | 18.8 | same-shape | (2, 6)→(2, 6) | `p=lambda g:[g:=[*zip(*g)][0]*3,g[::-1]]` |
| **322** | 18.8 | same-shape | (3, 3)→(3, 3) | `p=lambda g:g and p(g[:-1])+[[*map(max,*g*2)]]` |
| **314** | 18.8 | same-shape | (8, 8)→(8, 8) | `p=lambda a,r=range(8):[[max((C:=a[B])[A],C[A-3]&C[A-5],a[B-3][A]&a[B-5][A])for A in r]for B in r]` |
| **129** | 18.9 | same-shape | (3, 3)→(3, 3) | `p=lambda j:[[max(x:=sum(j,[]),key=x.count)]*3]*3` |
| **272** | 18.9 | same-shape | varies→varies | `p=lambda g,k=3:-k*g or p([[(A\|A*B>>2)-(A>1>k)for(A,B)in zip(A,(0,)+A)]for A in zip(*g[::-1])],k-1)` |
| **393** | 18.9 | shape-changes | (12, 12)→(3, 1) | `p=lambda g:[*zip(sorted({*(A:=sum(g,[]))},key=A.count)[2::-1])]` |
| **144** | 18.9 | shape-changes | (9, 4)→(4, 4) | `p=lambda g:[[3>>sum(A)for A in A]for A in map(zip,g,g[5:])]` |
| **087** | 19.1 | same-shape | (3, 3)→(3, 3) | `p=lambda j:[r[::-1]for r in j[::-1]]` |
| **140** | 19.1 | same-shape | (3, 3)→(3, 3) | `p=lambda j:[r[::-1]for r in j[::-1]]` |
| **135** | 19.1 | shape-changes | (9, 9)→(3, 3) | `p=lambda g:[r[6:]for r in g[:3]]` |
| **186** | 19.1 | same-shape | (3, 3)→(3, 3) | `p=lambda a,z=[0]*3:[(a:=[2]*sum(sum(a,z))+z)[:3],[0,a[3],0],z]` |
| **067** | 19.2 | shape-changes | varies→varies | `p=lambda g:[a[:len(g)]for a in g]` |
| **073** | 19.3 | same-shape | (5, 5)→(5, 5) | `p=lambda j:j[:1]*3+[j[3],[5-A*4for A in j[2]]]` |
| **149** | 19.5 | shape-changes | (11, 11)→(3, 3) | `p=lambda g:g and[[8<sum(sum(B[A:A+3])for B in g[:3])for A in(0,4,8)]]+p(g[4:])` |
| **056** | 19.6 | shape-changes | (3, 3)→(1, 1) | `p=lambda g:[[3-g[0].index(0)<<all(g[1])]]` |
| **261** | 19.7 | same-shape | varies→varies | `p=lambda a:[[c%6for c in r]for r in[a.pop()]+a]` |
| **103** | 19.8 | shape-changes | (3, 3)→(1, 1) | `p=lambda j:[[j==j[::-1]or 7]]` |
| **258** | 19.9 | same-shape | varies→varies | `import re p=lambda g:eval(re.sub('1, 0(?=, 1)','1,2',str(g)))` |
| **326** | 19.9 | shape-changes | varies→(2, 2) | `p=lambda j:[j[0][:2],j[1][:2]]` |
| **223** | 20.5 | shape-changes | (3, 3)→(9, 9) | `p=lambda g:g and[sum(zip(*g[:1]*3),())]*3+p(g[1:])` |
| **307** | 21.3 | shape-changes | varies→varies | `p=lambda g:g and[sum(zip(*g[:1]*2),())]*2+p(g[1:])` |
| **053** | 21.6 | same-shape | (3, 3)→(3, 3) | `p=lambda a:(a+a)[2:5]` |
| **113** | 21.6 | same-shape | varies→varies | `p=lambda j:j[:5]+j[4::-1]` |
| **116** | 21.6 | shape-changes | (3, 4)→(6, 4) | `p=lambda j:j[::-1]+j` |
| **164** | 21.6 | shape-changes | (3, 3)→(3, 6) | `p=lambda j:[R+R[::-1]for R in j]` |
| **172** | 21.6 | shape-changes | (3, 3)→(6, 3) | `p=lambda j:j+j[::-1]` |
| **210** | 21.6 | shape-changes | (3, 3)→(6, 3) | `p=lambda j:j+j[::-1]` |
| **311** | 21.6 | shape-changes | (3, 3)→(3, 6) | `p=lambda j:[R+R[::-1]for R in j]` |
| **385** | 21.6 | same-shape | (10, 4)→(10, 4) | `p=lambda j:j[:4:-1]+j[5:]` |
| **016** | 22.7 | same-shape | (3, 3)→(3, 3) | `p=lambda a:[[n^1+7%-~n//2^5for n in a[0]]]*3` |
| **276** | 22.7 | same-shape | varies→varies | `p=lambda g:eval(str(g).replace(*"62"))` |
| **309** | 22.7 | same-shape | varies→varies | `p=lambda j:eval(str(j).replace(*'75'))` |
| **337** | 22.7 | same-shape | varies→varies | `p=lambda j:eval(str(j).translate({53:56,56:53}))` |
| **179** | 25.0 | same-shape | (3, 3)→(3, 3) | `p=lambda g:[*zip(*g)]` |
| **241** | 25.0 | same-shape | varies→varies | `p=lambda j:[*zip(*j)]` |
