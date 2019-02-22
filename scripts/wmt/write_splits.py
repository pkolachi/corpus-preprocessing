#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ;

import sys ;
import os ; 

if len(sys.argv) < 3 :
  print("{0} <tsv-file-with-ids> <output-directory>".format(sys.argv[0])) ; 
  sys.exit(10) ; 

if not os.path.isdir(sys.argv[2]) :
  os.makedirs(sys.argv[2]) ; 

lns  = (ln.strip() for ln in ru.lines_from_file(sys.argv[1])) ; 
tlns = (X.split('\t', 1) for X in lns) ; 
tcns = ((X[0][1:].split(':',2), X[1]) for X in tlns) ; 
tcns = (("{0}.clean.{1}.txt".format(X[0][0], X[0][1].replace('.', '')), X[1]) for X in tcns) ; 

sid  = None ; 
lbuf = [] ;
for X in tcns :
  if X[0] != sid and sid : 
    # write output 
    ofpth = os.path.join(sys.argv[2], sid) ; 
    ru.lines_to_file(ofpth, lbuf) ; 
    lbuf = [] ; 
    # set new sid
  sid = X[0] ; 
  lbuf.append(X[1]) ; 

if lbuf :
  ofpth = os.path.join(sys.argv[2], sid) ; 
  ru.lines_to_file(ofpth, lbuf) ; 
  lbuf = [] ; 

