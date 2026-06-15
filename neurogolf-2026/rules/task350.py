p=lambda g:exec('g[:]=[[c or(1in r[:i])*(1in r[i:])*8for i,c in enumerate(r)]for r in zip(*g)];'*2)or g
