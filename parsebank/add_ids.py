#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ; 

import sys ; 
import os ; 

def main_loop() : 
  scount = 0 ;
  tok_buf  = [] ; 
  sent_buf = [] ; 
  MDELIM = ':'; # delimiter used in meta information
  for l in ru.lines_from_file(sys.argv[1]) : 
    if not l.strip() :
      scount += 1 ; 
      if orig_meta : 
        yield orig_meta ; 
        orig_meta = None ; 
      yield '# sent_id  = {0}'.format(scount) ;
      if len(tok_buf) and len(sent_buf) :
        tok_str = ' '.join(tok_buf) ; 
        yield '# tok_sent = {0}'.format(tok_str) ;
        yield '\n'.join(sent_buf) ; 
        yield l.strip() ; 
        tok_buf  = [] ; 
        sent_buf = [] ; 
    elif l.startswith('# ') :
      l  = l.strip('#') ; 
      l  = l.strip() ; 
      fs = l.split(MDELIM, 1) ; 
      if len(fs) > 1 : 
        fs[0] = fs[0].strip() ; 
        fs[1] = fs[1].strip() ; 
        orig_meta = '# {0} = {1}'.format('orighash'.ljust(8), fs[1]) ; 
      else :
        orig_meta = '# orig_id  = {0}'.format(fs[0]) ; 
    else :
      fs = l.split('\t') ; 
      sent_buf.append(l.strip()) ; 
      try : 
        _ = int(fs[0]) ; 
        tok_buf.append(fs[1]) ; 
      except ValueError : 
        # skip this line since it doesn't look like a regular token
        pass ;  

ru.lines_to_file(sys.argv[2], main_loop()) ;

