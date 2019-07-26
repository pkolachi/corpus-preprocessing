#!/usr/bin/env python3

from globalimports import * ; 
import random_utils as ru ; 
import sys ; 
import os ; 

cls = ru.lines_from_file(sys.argv[1], large=True) ; 
dhead = next(cls) ; 
tmpdir = sys.argv[2] ; 
if not os.path.isdir(tmpdir) : 
  os.mkdir(tmpdir) ; 
sentids = [] ; 
bfiles  = [] ; 

def split_chunks() :
  global bfiles ; 
  buf   = [] ; 
  shead = None ; 
  for l in cls : 
    if l.startswith('# sent_id') :
      _, sid = l.split('=', 1) ; 
      _, sp, si = sid.strip().split(':') ;
      sp = sp.strip() ; 
      si = si.strip() ; 
      sentids.append(si) ; 
      if sp != shead and shead :
        print("{0}-{1}".format(sp, shead), file=sys.stderr) ; 
        # empty buffer into 
        fpth = os.path.join(tmpdir, "{}.conllu".format(shead)) ; 
        ru.lines_to_file(fpth, buf) ; 
        bfiles.append(fpth) ; 
        buf = [] ;
      shead = sp ; 
    buf.append(l) ; 
  if len(buf) :
    fpth = os.path.join(tmpdir, "{}.conllu".format(shead)) ; 
    ru.lines_to_file(fpth, buf) ; 
    bfiles.append(fpth) ; 
    buf = [] ;

def merge_chunks() :
  global bfiles ; 
  global sentids ; 
  sidx = 0 ; 
  yield dhead ; 
  for fpth in sorted(bfiles) : 
    for l in ru.lines_from_file(fpth) : 
      if l.startswith('# sent_id') :
        pref, oldid = l.rsplit(':', 1) ; 
        yield "{0}:{1}".format(pref, sentids[sidx]) ;
        sidx += 1 ; 
      else:
        yield l ; 

split_chunks() ; 
ru.lines_to_file(sys.argv[3], merge_chunks()) ; 
