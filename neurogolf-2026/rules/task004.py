p=lambda j:[exec('i-=1;v,a[i]=a[i],0;a[i+any(b[i+1:])]+=v;'*(i:=len(a)))for(a,b)in zip(j,j[1:])]and j
