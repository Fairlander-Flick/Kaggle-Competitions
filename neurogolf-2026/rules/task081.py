import re
p=lambda a,k=3:a*-k or p([*zip(*eval(re.sub('0(?=, 8.{19}8, 8)','1',str(a)))[::-1])],k-1)
