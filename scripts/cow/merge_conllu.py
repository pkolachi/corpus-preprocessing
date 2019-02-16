#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ; 

import sys ; 
import os ; 

BATCH_SIZE  = 5000 ; 
BUNDLE_SIZE = 100 ;

def main_loop() : 
  splitsdir = sys.argv[1] ; 
  for arnm in sorted(os.listdir(splitsdir)) : 
    arpt = os.path.join(splitsdir, arnm) ;     # path to the archive file
    os.system('tar -xvzf {0} -C {1} 2> /dev/null'.format(arpt, splitsdir)) ; 
    ardr = os.path.splitext(arnm)[0] ; 
    ardp = os.path.join(splitsdir, ardr) ; # path to the extracted directory
    cfiles = sorted(os.listdir(ardp)) ; 
    cfps = [os.path.join(ardp, f) for f in cfiles] ;
    prev = None ; 
    for fp in cfps :
      c = 0 ; 
      for l in ru.lines_from_file(fp) :
        if not l.strip() :
          c += 1 ; 
        if l.startswith('# sent_id') : 
          # also check that sentences are in ascending order
          meta = l.split('=', 1)[1].strip().split('-') ;
          if prev and prev > meta :
            print("Sentence order is being messed up in {0}".format(fp), file=sys.stderr) ;
          prev = meta ; 
        yield l.strip() ; 
      if c != BATCH_SIZE : 
        print("File doesnot have sufficient sentences. {0}".format(fp), file=sys.stderr) ;
    #os.system('cat {0}'.format(' '.join(cfps))) ;
    os.system('rm -r {0}'.format(ardp)) ;

ru.lines_to_file(sys.argv[2], main_loop()) ;

