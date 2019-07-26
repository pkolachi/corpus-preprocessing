#!/usr/bin/env python3
import sys ; 

from globalimports import * ;
import random_utils as ru ; 

sids = dict((int(l),True) for l in ru.lines_from_file(sys.argv[1])) ;
fils = (l for i,l in enumerate(ru.lines_from_file(sys.argv[2]), start=1) if i in sids) ; 
ofil = sys.argv[3] if len(sys.argv) >= 4 else '' ; 
ru.lines_to_file(ofil, fils) ; 

