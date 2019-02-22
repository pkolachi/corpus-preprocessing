#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ; 

import sys ; 
import os ; 

BATCH_SIZE  = 5000 ; 
BUNDLE_SIZE = 100 ;

def main_loop() : 
  splitsdir = sys.argv[1] ;
  scount = 0 ;
  MDELIM = '='; # delimiter used in meta information
  for arnm in sorted(os.listdir(splitsdir)) : 
    arpt = os.path.join(splitsdir, arnm) ;     # path to the archive file
    os.system('tar -xvzf {0} -C {1} 2> /dev/null'.format(arpt, splitsdir)) ; 
    ardr = os.path.splitext(arnm)[0] ; 
    ardp = os.path.join(splitsdir, ardr) ; # path to the extracted directory
    cfiles = sorted(os.listdir(ardp)) ; 
    cfps = [os.path.join(ardp, f) for f in cfiles] ;
    prev = None ; 
    tok_buf  = [] ; 
    sent_buf = [] ; 
    for fp in cfps :
      c = 0 ; 
      for l in ru.lines_from_file(fp) :
        if not l.strip() :
          c += 1 ; 
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
            orig_meta = '# {0} = {1}'.format(fs[0].ljust(8), fs[1]) ; 
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
      if c != BATCH_SIZE : 
        print("File doesnot have sufficient sentences. {0}".format(fp), file=sys.stderr) ;
    #os.system('cat {0}'.format(' '.join(cfps))) ;
    os.system('rm -r {0}'.format(ardp)) ;

ru.lines_to_file(sys.argv[2], main_loop()) ;

