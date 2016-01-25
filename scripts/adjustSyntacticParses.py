#!/usr/bin/env python3

from __future__ import print_function;
try:
  from globalimports import *;
  import random_utils;
except ImportError:
  sys.exit(1);

def addEmptyParses(const_parses_file, empty_sent_ids):
  empty_sent_ids = dict([ (int(line.strip()), True) \
      for line in random_utils.lines_from_file(empty_sent_ids) ]);
  sent_count = 0;
  for line in random_utils.lines_from_file(const_parses_file):
    sent_count += 1;
    while empty_sent_ids.has_key(sent_count):
      print('(ROOT ())', file=stdout);
      sent_count += 1;
    print(line.strip(), file=stdout);
  return;

def removeEmptyParses(const_parses_file, empty_sent_ids):
  empty_sent_ids = dict([ (int(line.strip()), True) \
      for line in random_utils.lines_from_file(empty_sent_ids) ]);
  print(len(empty_sent_ids), file=stderr);
  sent_count = 0;
  tmp_count = 0;
  for line in random_utils.lines_from_file(const_parses_file):
    sent_count += 1;
    if sent_count in empty_sent_ids:
      tmp_count += 1;
      print(line.strip(), file=stdout);
    print("%d\t%d" %(sent_count, tmp_count), file=stderr);
  return;

if __name__ == '__main__':
  const_parses_file, empty_sent_ids = sysargv[1], sysargv[2];
  #addEmptyParses(const_parses_file, empty_sent_ids);
  removeEmptyParses(const_parses_file, empty_sent_ids);
