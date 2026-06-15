import re
s=re.sub
p=lambda g:eval(s('(?<!1, )1(, 0)+, 1',lambda m:s('0','27'[len(m[0])%2],m[0]),str(g)))
