#!/usr/bin/env python

from __future__ import print_function;
try:
  from globalimports import *
  import parallelize_utils as pu;
  import random_utils as ru;
except ImportError:
  print("Missing necessary module 'random_utils' and 'parallelize_utils' \
    for this script");
  sys.exit(1);

import argparse;
import multiprocessing;
import re;
import sys;
import time;

def read_mapping(mapfile):
  map_tags = {};
  for line in ru.lines_from_file(mapfile):
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
    possible_matches = [key for key in 
      filter(lambda X: X[0] == tag, mapping.keys())];
    if len(possible_matches) > 1 and idx > 0:
      best_match = [key for key in
        filter(lambda X: X[1] == tag_sequence[idx-1], \
          filter(lambda X: len(X) == 2, possible_matches) )
        ];
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

def convert_tagged_text(gposmapfile, tagged_file='',
    keepTags=True, threads=2, delim=''):
  global map_tag;
  map_tag = read_mapping(gposmapfile);

  delimold = delimnew = '_' if not delim else delim;
  bufferSize = 50000;
  if threads > 1:
    pool = multiprocessing.Pool(threads, maxtasksperchild=1000);

  if keepTags:
    def outputWriter(args):
      forms, tags = args;
      return ' '.join(
        u"{0}{1}{2}".format(x, delimnew, y)
        for x, y in zip(forms, tags)
        );
  else:
    def outputWriter(forms):
      return u" ".join(x for x in forms);

  inputStream = ru.lines_from_file(tagged_file);
  ws = re.compile('\s+', flags=re.U);
  inputStream = map(lambda X: 
      list(tuple(tok.rsplit(delimold, 1)) if tok.find(delimold) != -1 \
        else (tok, '_UNK_') \
      for tok in re.split(ws, X)), inputStream);

  oldtime, newtime = time.time(), time.time();
  while True:
    inputBuffer = list(islice(inputStream, bufferSize));
    formsBuffer = [[x for x, y in sentence] for sentence in inputBuffer];
    tagsBuffer  = [[y for x, y in sentence] for sentence in inputBuffer];

    if keepTags and threads > 1:
      outputBuffer = zip(
        formsBuffer, 
        pool.imap(convert, tagsBuffer, chunksize=10000)
        );
    elif keepTags and threads <= 1:
      outputBuffer = zip(formsBuffer, map(convert, tagsBuffer));
    else:
      outputBuffer = formsBuffer;
    
    for out in map(outputWriter, outputBuffer): yield out;
    if len(inputBuffer) < bufferSize: break;
    newtime = time.time();
    print("Dumping tags in %.5f"%(newtime-oldtime), file=sys.stderr);
    oldtime = newtime;

  if threads > 1:
    pool.close();
  return;

def cmdLineParser():
  argparser = argparse.ArgumentParser(
      prog='unigoogle_utils.py', 
      description='Convert tagged corpora to UD tagset',
      );
  argparser.add_argument('-m', '--mapping', dest='mapping_file',
      required=True, help='');
  argparser.add_argument('-i', '--input', dest='input_file',
      default='', help='');
  argparser.add_argument('-o', '--output', dest='output_file',
      default='', help='');
  argparser.add_argument('-d', '--delim', dest='delim',
      default=u'_', help='');
  argparser.add_argument('-t', '--threads', dest='threads',
      type=int, default=1, help='');
  argparser.add_argument('-s', '--strip-tags', dest='keepTags',
      action='store_false', default=True, help='');
  argparser.add_argument('-f', '--format', dest='format',
      choices=['txt', 'conll07', 'conll09', 'conllu'], default='txt',
      help='');
  return argparser;

if __name__ == '__main__':
  prog_opts = cmdLineParser().parse_args(sysargv[1:]);
  tagged_sequences = convert_tagged_text(
    prog_opts.mapping_file,
    prog_opts.input_file,
    keepTags=prog_opts.keepTags,
    delim=prog_opts.delim,
    threads=prog_opts.threads,
    );

  if prog_opts.format in ['conll07', 'conll09', 'conllu']:
    import conll_utils as cu;
    cu.FIELDS = \
      cu.CONLL07_COLUMNS if prog_opts.format == 'conll07' \
      else cu.CONLL09_COLUMNS if prog_opts.format == 'conll09' \
      else cu.CONLLU_COLUMNS ;
    sents = cu.tagged_to_sentences(tagged_sequences, delim=prog_opts.delim);
    lines = cu.sentences_to_conll(sents);
  else:
    lines = tagged_sequences;

  ru.lines_to_file(prog_opts.output_file, lines);
  sysexit(0);
