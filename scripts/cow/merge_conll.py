#!/usr/bin/env python3

from globalimports import *;
import random_utils as ru ;
import conll_utils  as cu ;

with ru.smart_open(sysargv[1], 'wb') as outfile:
  cu.FIELDS = cu.CONLL07_COLUMNS;
  for filename in sysargv[2:]:
    with ru.smart_open(filename) as infile:
      ru.lines_to_filehandle(outfile, \
          cu.sentences_to_conll07(cu.sentences_from_conll(infile))) ;

