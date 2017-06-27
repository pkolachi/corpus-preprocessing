#!/usr/bin/env python2

from builtins    import xrange as range;
from builtins    import raw_input as input;
from collections import defaultdict;
from itertools   import \
  imap    as map, \
  ifilter as filter, \
  izip    as zip, \
  count   as counter, \
  repeat  as replicate, \
  islice, starmap;
from operator    import itemgetter;
from sys         import \
  argv   as sysargv, \
  stdin  as sysin, \
  stdout as sysout, \
  stderr as syserr, \
  exit   as sysexit;

import re;
WSPAT  = re.compile('\s+', flags=re.U);
TABPAT = re.compile('\t',  flags=re.U);

# -- this is now obsolete; 
# -- instead random_utils takes care of encoding issues for all streams
#import codecs;
#stdin  = codecs.getreader('utf-8')(stdin);
#stdout = codecs.getwriter('utf-8')(stdout);
#stderr = codecs.getwriter('utf-8')(stderr);

