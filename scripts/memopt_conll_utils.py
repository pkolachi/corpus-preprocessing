#!/usr/bin/env python

"""
 An alternate implementation of conll_utils, with additional memory 
 optimizations. The module does not use lazyness, instead it relies on 
 namedtuple to reduce memory usage, when the entire CoNLL dataset needs to 
 be loaded.
"""

from __future__ import print_function, division;
try:
  from globalimports import *;
  from random_utils import llnum2name as llnum2name;
  import random_utils;
except ImportError:
  sys.exit(1);
  llnum2name = lambda x: str(x);

from collections import namedtuple;

# These are the labels on the columns in the CoNLL 2007 dataset.
CONLL07_COLUMNS = ('id', 'form', 'lemma', \
    'cpostag', 'postag', 'feats', \
    'head', 'deprel', \
    'phead', 'pdeprel', )
# These are the labels on the columns when constituency parser out is
# converted to dependency format
AUG_CONLL07_COLUMNS = ('id', 'form', 'lemma', \
    'cpostag', 'postag', 'const_parse', 'feats', \
    'head', 'deprel', \
    'phead', 'pdeprel', )
# These are the labels on the columns in the CoNLL 2009 dataset.
CONLL09_COLUMNS = ('id', 'form', 'lemma', 'plemma', \
    'postag', 'ppostag', 'feats', 'pfeats', \
    'head', 'phead', 'deprel', 'pdeprel', 'fillpred', 'sense', )
# These are the labels on the columns in the CoNLL 2009 dataset.
BERKELEY_COLUMNS = ('form', 'cpostag');
# These are the labels on the morfette tagger
MORFETTE_COLUMNS = ('form', 'lemma', 'postag');

FIELDS = CONLL07_COLUMNS;
CoNLLFields = namedtuple('CoNLLFields', FIELDS);
BUF_SIZE = 100000;

def set_fields(format):
  global FIELDS, CoNLLFields;
  FIELDS = format;
  CoNLLFields = namedtuple('CoNLLFields', FIELDS);
  return;
  
def words_from_conll(lines, fields):
  '''Read words for a single sentence from a CoNLL text file.'''
  global FIELDS, CoNLLFields
  if fields != FIELDS:
    CoNLLFields = namedtuple('CoNLLFields', FIELDS);
  columnsList = [map(lambda X: X if X != '_' else None, \
      line.split('\t')) for line in lines];
  return tuple(CoNLLFields(*columns) for columns in columnsList);

def lines_from_conll(lines, comments=False):
  '''Read lines for a single sentence from a CoNLL text file.'''
  for line in lines:
    if not line.strip():
      return;
    if comments and line.startswith('#'):
      continue;
    else:
      yield line.strip();

def sentences_from_conll(handle, comments=False):
  '''Read sentences from lines in an open CoNLL file handle.'''
  global FIELDS, CoNLLFields;
  CoNLLFields = namedtuple('CoNLLFields', FIELDS);
  sent_count = 0;
  while True:
    lines = tuple(lines_from_conll(handle, comments));
    if not len(lines):
      break;
    sent_count += 1;
    yield words_from_conll(lines, fields=FIELDS);
    if not sent_count%BUF_SIZE:
      print("(CoNLL:%s)" %(llnum2name(sent_count)), file=stderr, end=' ');
  print("(CoNLL:%s)" %(llnum2name(sent_count)), file=stderr);

def words_to_conll(sent, fields=CONLL07_COLUMNS):
  global FIELDS, CoNLLFields
  if fields != FIELDS:
    CoNLLFields = namedtuple('CoNLLFields', FIELDS);
  str_repr = [];
  if type(sent) == type(()) and len(sent) == 2:
    str_repr.append(str(sent[0]));
    sent = sent[1];
  for token in sent:
	str_repr.append( '\t'.join( map(lambda X: str(X) if X else '_', [getattr(token, feat) for feat in fields]) ) );
  return '\n'.join(str_repr);

def sentences_to_conll07(handle, sentences):
  for sent_idx, sent in enumerate(sentences, start=1):
    print(words_to_conll(sent, fields=CONLL07_COLUMNS), file=handle);
    print("", file=handle);
    if not sent_idx%BUF_SIZE: 
      print("(%s)" %(llnum2name(sent_idx)), file=stderr, end=' ');
  print("(%s)" %(llnum2name(sent_idx)), file=stderr);
  return;

def sentences_to_conll09(handle, sentences):
  for sent_idx, sent in enumerate(sentences, start=1):
    print(words_to_conll(sent, fields=CONLL09_COLUMNS), file=handle);
    print("", file=handle);
    if not sent_idx%BUF_SIZE: 
      print("(%s)" %(llnum2name(sent_idx)), file=stderr, end=' ');
  print("(%s)" %(llnum2name(sent_idx)), file=stderr);
  return;
