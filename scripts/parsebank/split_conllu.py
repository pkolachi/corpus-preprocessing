#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru   ; 
import os.path ; 
import sys ; 
import os ; 

if not os.path.isdir(sys.argv[2]) : 
  os.makedirs(sys.argv[2]) ; 
cls = ru.lines_from_file(sys.argv[1]) ; 

def main_loop() :
  BATCH_SIZE  = 5000 ;   # no. of sentences in one chunk 
  BUNDLE_SIZE = 100 ;    # no. of files     in one directory
  lines       = [] ; 
  sentc       = 0  ;
  batchdirs   = [] ; 
  for l in cls : 
    if not l.strip() :
      sentc += 1 ; 
      lines.append(l.strip()) ; 
      if not (sentc % BATCH_SIZE) : 
        # write all sentences to buffer
        bid  = int(sentc/BATCH_SIZE) ;
        buid = int(bid  /BUNDLE_SIZE) ;
        dirp = os.path.join(sys.argv[2], str(buid).zfill(4)) ;
        if not os.path.isdir(dirp) :
          os.makedirs(dirp) ; 
          batchdirs.append(dirp) ; 
          # allow compression of previous batch directories from time to time
          if len(batchdirs) > 10 : 
            for bdir in batchdirs[:-2] :
              #os.system("tar -cvzf {0}.tgz {0}".format(bdir)) ; 
              #os.system("rm -r {0}".format(bdir)) ; 
              pass 
            batchdirs = batchdirs[-2:] ; 

        outp = os.path.join(dirp, '{0}_split{1}.conllu'.format(sys.argv[3], str(bid).zfill(7))) ;
        ru.lines_to_file(outp, lines) ; 
        # reset everything
        lines   = [] ;
    else :
      lines.append(l.strip()) ;

  # for all remaining sentences ; 
  bid  = int(sentc/BATCH_SIZE )+1 ;
  buid = int(bid  /BUNDLE_SIZE) ;
  dirp = os.path.join(sys.argv[2], str(buid).zfill(4)) ;
  if not os.path.isdir(dirp) :
    os.makedirs(dirp) ; 
  outp = os.path.join(dirp, '{0}_split{1}.conllu'.format(sys.argv[3], str(bid).zfill(7))) ;
  ru.lines_to_file(outp, lines) ;
  for bdir in batchdirs : 
    #os.system("tar -cvzf {0}.tgz {0}".format(bdir)) ; 
    #os.system("rm -r {0}".format(bdir)) ; 
    pass ; 

  return ; 

main_loop() ; 
