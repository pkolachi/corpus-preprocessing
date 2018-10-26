#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ; 
import sys ; 


def main_loop(start, end) :
  meta = None ; 
  for line in ru.lines_from_file(sys.argv[1], large=True) :
    if line.startswith('# sent_id') : 
      lid  = line.split('=')[1].strip() ; 
      meta = lid.split('-') ;
      meta = (meta[0], int(meta[1])) ; 
      if start < meta < end : 
        yield line.strip() ;
    elif start < meta < end :
      yield line.strip() ; 

ru.lines_to_file(sys.argv[-1], main_loop(('nlcow14ax07',38091056), ('nlcow14ax07', 38096066))) 

