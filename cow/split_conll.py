#!/usr/bin/env python

try :
  import sys ; 
  assert(sys.version_info >= (3,0)) ;
  from globalimports import * ;
  import random_utils as ru ;
except AssertionError :
  from py2_globalimports import * ; 
  import py2_random_utils as ru ; 

import conll_utils ;
import itertools as it ; 

end = False ;
with ru.smart_open(sysargv[1]) as infile :
  cu.FIELDS   = cu.CONLL07_COLUMNS ;
  conll_sents = cu.sentences_from_conll(infile) ;
  idx = 1 ;
  while True :
    outfilename = 'nlcow14ax_part{0}.matetagged.conll.bz2'.format(str(idx).zfill(3)) ;
    with ru.smart_open(outfilename, 'wb') as outfile:
      for _ in xrange(10) :
        part_buf = list(islice(conll_sents, 100000)) ;
		conll_utils.sentences_to_conll07(outfile, part_buf) ;
	  if len(part_buf) < 100000 :
		    end = True ;
		    break ;
	if end:
	    break;
	idx += 1;


