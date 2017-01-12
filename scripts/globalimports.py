#!/usr/bin/env python

from __future__ import print_function, division;
try:
  from itertools import imap as map, \
      ifilter as filter, \
      izip as zip, \
      islice, starmap, \
      count as counter, \
      repeat as replicate;
  from builtins import xrange as range;
  from builtins import raw_input as input;
except ImportError:
  from itertools import islice, starmap, \
      count as counter, \
      repeat as replicate;
from collections import defaultdict;
from operator import itemgetter;
from sys import argv as sysargv, stdin, stdout, stderr, exit as sysexit;

import re;
WSPAT  = re.compile('\s+', flags=re.U);
TABPAT = re.compile('\t',  flags=re.U);

#import codecs;
#stdin  = codecs.getreader('utf-8')(stdin);
#stdout = codecs.getwriter('utf-8')(stdout);
#stderr = codecs.getwriter('utf-8')(stderr);

