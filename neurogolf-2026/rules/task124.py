p=lambda a,k=6:(A:=[(A//(B:=k//3)*(k%3)*[0]+a[A%B])[:10]for A in range(10)])*(A[:5]==a[:5])or p(a,-~k)
