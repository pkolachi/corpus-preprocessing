
from __future__ import print_function
try:
  from itertools import ifilter, imap, islice, izip, starmap, count as counter, repeat as replicate;
except ImportError:
  from itertools import starmap, count as counter, repeat as replicate;
  from builtins import filter as ifilter, map as imap, zip as izip, range as xrange;
from collections import defaultdict;
from operator import itemgetter;
from sys import argv as sysargv, stdin, stdout, stderr, exit as sysexit;

import codecs;
stdin  = codecs.getreader('utf-8')(stdin);
stdout = codecs.getwriter('utf-8')(stdout);
stderr = codecs.getwriter('utf-8')(stderr);

