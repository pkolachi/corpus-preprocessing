
from __future__ import print_function
try:
  from itertools import imap as map, \
      ifilter as filter, \
      izip as zip, \
      islice, starmap, \
      count as counter, \
      repeat as replicate;
  from builtins import xrange as range;
except ImportError:
  from itertools import islice, starmap, \
      count as counter, \
      repeat as replicate;
from collections import defaultdict;
from operator import itemgetter;
from sys import argv as sysargv, stdin, stdout, stderr, exit as sysexit;

import codecs;
stdin  = codecs.getreader('utf-8')(stdin);
stdout = codecs.getwriter('utf-8')(stdout);
stderr = codecs.getwriter('utf-8')(stderr);

