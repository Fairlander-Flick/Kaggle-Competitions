p=lambda g:exec('d=[*map(max,g)].index(8);g[:]=zip(*(sorted(g[:d],key=any)+g[d:])[::-1]);'*4)or g
