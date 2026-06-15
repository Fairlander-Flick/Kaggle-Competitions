import re
p=lambda g:[[int(re.split('([^0]), (0, )+\\1',str(g))[1])]]
