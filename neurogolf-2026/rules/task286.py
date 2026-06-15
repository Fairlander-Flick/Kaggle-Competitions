import re
p=lambda g:exec('g[:]=zip(*eval(re.sub("0(?=, ([^08]))",r"%d-\\1",str(g)))[::-1]);'%(sum({*sum(g,[])})-8)*444)or g
