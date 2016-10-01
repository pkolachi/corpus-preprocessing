#!/usr/bin/env python

from __future__ import print_function;
try:
  from globalimports import *
  import random_utils, parallelize_utils;
except ImportError:
  print("Missing necessary module 'random_utils' and 'parallelize_utils' \
      for this script");
  sys.exit(1);

import multiprocessing, re, sys, time;


def read_mapping(mapfile):
  map_tags = {};
  for line in random_utils.lines_from_file(mapfile):
    line = line.strip();
    fine, coarse = line.split('\t');
    fine = (fine, ) if fine.find('|') == -1 else tuple(fine.split('|'));
    map_tags[fine] = coarse;
  return map_tags;

def convert(tag_sequence, mapping=None):
  global map_tag;
  if not mapping:
    mapping = map_tag;
  coarse_sequence = [];
  for idx, tag in enumerate(tag_sequence):
    possible_matches = [key for key in \
        filter(lambda X: X[0] == tag, mapping.keys())];
    if len(possible_matches) > 1 and idx > 0:
      best_match = [key for key in \
          filter(lambda X: X[1] == tag_sequence[idx-1], \
          filter(lambda X: len(X) == 2, possible_matches))];
      if len(best_match) < 1: 
        best_match = [key for key in \
            filter(lambda X: len(X) == 1, possible_matches)];
      coarse_sequence.append( mapping[best_match[0]] );
    elif tag == '_UNK_' or len(possible_matches) == 0:
      coarse_sequence.append( 'X' );
    else:
      coarse_sequence.append( mapping[possible_matches[0]] );
  return coarse_sequence;

map_tag = defaultdict(lambda:'X');

def convert_tagged_text(*args):
  if len(args) < 1:
    print("./%s <map-file>" %(sys.argv[0]), file=sys.stderr);
    sys.exit(1);

  global map_tag;
  map_tag = read_mapping(args[0]);
  inputFileName  = args[1] if len(args) >= 2 else '';
  outputFileName = args[2] if len(args) >= 3 else '';
  delimold = delimnew = '_';
  formsBuffer, tagsBuffer, bufferSize = [], [], 100000;

  keepTags = True;
  threads = 2;

  if threads > 1:
    pool = multiprocessing.Pool(threads, maxtasksperchild=1000);

  if keepTags:
    outputWriter = lambda X, Y: \
        ' '.join(["%sc%s" %(x, delimnew, y) for x, y in zip(X, Y)]);
  else:
    outputWriter = lambda X: ' '.join(["%s" %x for x in X]);

  oldtime, newtime = time.time(), time.time();
  with random_utils.smart_open(inputFileName) as inputFile, \
      random_utils.smart_open(outputFileName, mode='wb') as outputFile:
    inputStream = map(lambda X: (tuple(tok.rsplit(delimold, 1)) \
        if tok.find(delimold) != -1 \
        else (tok, '_UNK_') \
        for tok in re.split('\s+', X.strip())), inputFile);

    while True:
      inputBuffer = islice(inputStream, bufferSize);
      for line_count, line in enumerate(inputBuffer):
        current_forms = [tok[0] for tok in line];
        formsBuffer.append(current_forms);
        if keepTags:
          current_tags = [tok[1] for tok in line];
          tagsBuffer.append(current_tags);
      if keepTags and threads > 1:
        outputBuffer = zip(formsBuffer, \
            pool.imap(convert, tagsBuffer, chunksize=10000));
      elif keepTags and threads <= 1:
        outputBuffer = zip(formsBuffer, map(convert, tagsBuffer));
      else:
        outputBuffer = formsBuffer;
      random_utils.lines_to_filehandle(outputFile, \
          map(outputWriter, outputBuffer));
      if line_count < bufferSize:
        break;
      formsBuffer, tagsBuffer, bufferSize = [], [], 0;
      newtime = time.time();
      print("Dumping tags in %.5f"%(newtime-oldtime), file=sys.stderr);
      oldtime = newtime;

  if threads > 1:
    pool.close();

  return;

if __name__ == '__main__':
  convert_tagged_text(*sys.argv[1:]);
