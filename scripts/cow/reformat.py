#!/usr/bin/env python3

from   globalimports import * 
import random_utils as ru 

import sys ; 

sentids = ru.lines_from_file(sys.argv[1]) ; 
start   = True ; 
for line in sys.stdin :
  if start :
    sids = next(sentids) ;
    print("# sent_id  = {0}".format(sids)) ;
    start = False ; 
  if not line.strip() :
    print("") ;
    start = True ;
  else:
    print(line.strip()) ;
