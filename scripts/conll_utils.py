#!/usr/bin/env python

from __future__ import print_function, division;
try:
  from globalimports import *;
  from random_utils import llnum2name as llnum2name;
  import random_utils;
except ImportError:
  sys.exit(1);
  llnum2name = lambda x: str(x);

# These are the labels on the columns in the CoNLL 2007 dataset.
CONLL07_COLUMNS = ('id', 'form', 'lemma', 'cpostag', 'postag', 'feats', 'head', 'deprel', 'phead', 'pdeprel', )
AUG_CONLL07_COLUMNS = ('id', 'form', 'lemma', 'cpostag', 'postag', 'const_parse', 'feats', 'head', 'deprel', 'phead', 'pdeprel', )
# These are the labels on the columns in the CoNLL 2009 dataset.
CONLL09_COLUMNS = ('id', 'form', 'lemma', 'plemma', 'postag', 'ppostag', 'feats', 'pfeats', 'head', 'phead', 'deprel', 'pdeprel', 'fillpred', 'sense', )
# These are the labels on the columns in the CoNLL 2009 dataset.
BERKELEY_COLUMNS = ('form', 'cpostag');
# These are the labels on the morfette tagger
MORFETTE_COLUMNS = ('form', 'lemma', 'postag');
FIELDS = CONLL07_COLUMNS;
#FIELDS = MORFETTE_COLUMNS;

BUF_SIZE = 100000;

def words_from_conll(lines, fields):
  '''Read words for a single sentence from a CoNLL text file.'''
  return [dict(zip(fields, line.split('\t'))) for line in lines];

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
  global FIELDS;
  sent_count = 0;
  while True:
    lines = tuple(lines_from_conll(handle, comments));
    if not len(lines):
      break;
    sent_count += 1;
    if not sent_count%BUF_SIZE:
      print("(CoNLL:%s)" %(llnum2name(sent_count)), file=stderr, end=' ');
    yield words_from_conll(lines, fields=FIELDS);
  print("(CoNLL:%s)" %(llnum2name(sent_count)), file=stderr);

def words_to_conll(sent, fields=CONLL07_COLUMNS):
  str_repr = [];
  if type(sent) == type(()) and len(sent) == 2:
    str_repr.append( '#'+str(sent[0]) );
    sent = sent[1];
  for token in sent:
    feat_repr = '|'.join(['%s=%s' %(key, token['feats'][key]) for key in sorted(token['feats'].keys())]) if token.has_key('feats') and type(token['feats']) == type({}) else token.get('feats', '_');
    token['feats'] = feat_repr if feat_repr.strip() else '_';
    str_repr.append( '\t'.join([token.get(feat, '_') for feat in fields]) );
  return '\n'.join(str_repr);

def sentences_to_conll07(handle, sentences):
  global CONLL07_COLUMNS;
  if not sentences:
    print("(CoNLL07:%s)" %(llnum2name(0)), file=stderr);
    return;
  for sent_idx, sent in enumerate(sentences, start=1):
    print(words_to_conll(sent, fields=CONLL07_COLUMNS), file=handle);
    print("", file=handle);
    if not sent_idx%BUF_SIZE: 
      print("(CoNLL07:%s)" %(llnum2name(sent_idx)), file=stderr, end=' ');
  print("(CoNLL07:%s)" %(llnum2name(sent_idx)), file=stderr);
  return;

def sentences_to_conll09(handle, sentences):
  global CONLL09_COLUMNS;
  if not sentences:
    print("(CoNLL09:%s)" %(llnum2name(0)), file=stderr);
    return;
  for sent_idx, sent in enumerate(sentences, start=1):
    print(words_to_conll(sent, fields=CONLL09_COLUMNS), file=handle);
    print("", file=handle);
    if not sent_idx%BUF_SIZE: 
      print("(CoNLL09:%s)" %(llnum2name(sent_idx)), file=stderr, end=' ');
  print("(CoNLL09:%s)" %(llnum2name(sent_idx)), file=stderr);
  return;

def sentences_to_conll(handle, sentences):
  if not sentences:
    print("(CoNLL:%s)" %(llnum2name(0)), file=stderr);
    return;
  global FIELDS;
  for sent_idx, sent in enumerate(sentences, start=1):
    print(words_to_conll(sent, fields=FIELDS), file=handle);
    print("", file=handle);
    if not sent_idx%BUF_SIZE: 
      print("(CoNLL:%s)" %(llnum2name(sent_idx)), file=stderr, end=' ');
  print("(CoNLL:%s)" %(llnum2name(sent_idx)), file=stderr);
  return;

def sentences_to_tok(handle, sentences):
  for sent_idx, sent in enumerate(sentences, start=1):
    print(" ".join([token['form'] for token in sent]), file=handle);
  return;

def sentences_to_propercased(handle, sentences):
  for sent_idx, sent in enumerate(sentences, start=1):
    print(" ".join([token['form'].lower() if token['feats'].find('nertype') == -1 and token['form'] != 'I' else token['form'] for token in sent]), file=handle);
  return;

def sentences_to_tagged(handle, sentences):
  delim = '|';
  for sent_idx, sent in enumerate(sentences, start=1):
    metaInfo = False;
    if type(sent) == type(()) and len(sent) == 2:
      # input is a tuple, with meta-information and actual sentence;
      metaInfo = True;
      sentinfo, sent = sent[0], sent[1];
    print('%s%s' %(repr(sentinfo)+'\t' if metaInfo else '', " ".join(['%s%c%s'%(token['form'], delim, token['cpostag']) for token in sent])), file=handle);
  return;

def tokenized_to_sentences(sentences):
  import re;
  global FIELDS;
  FIELDS = CONLL09_COLUMNS;
  for sent_idx, sent in enumerate(sentences, start=1):
    if not sent.strip():
      continue;
    tokens = re.split('\s+', sent.strip());
    conll_sent = [];
    if not len(tokens):
      print('warning: empty sentence at %d' %(sent_idx));
      continue;
    for tok_idx, tok in enumerate(tokens, start=1):
      conll_edge = {'form': tok, 'id': str(tok_idx)};
      conll_sent.append(conll_edge);
    yield conll_sent;

def tagged_to_sentences(sentences):
  global FIELDS;
  delim = '_';
  FIELDS = CONLL09_COLUMNS;
  for sent_idx, sent in enumerate(sentences, start=1):
    tokens = re.split('\s+', sent);
    conll_sent = [];
    for tok_idx, tok in enumerate(tokens):
      try:
        form, pos = tok.rsplit(delim, 1);
      except ValueError:
        form, pos = tok, 'X';
      conll_edge = {'form': form, 'id': str(tok_idx+1)};
      pos_key = 'ppostag' if FIELDS == CONLL09_COLUMNS else 'cpostag' 
      conll_edge[pos_key] = pos;
      conll_sent.append(conll_edge);
    yield conll_sent;

def prepare_web_version(sentences):
  global FIELDS;
  predposfieldname = 'ppostag' if FIELDS == CONLL09_COLUMNS else 'cpostag';
  goldposfieldname = 'postag';
  for sent in sentences:
    for token in sent:
      if token[predposfieldname] == '_' and token[goldposfieldname] != '_':
        token[predposfieldname] = token[goldposfieldname];
      for field in token.keys():
        if field not in ('id', 'form', predposfieldname):
          del token[field];
    yield sent;

def __constparse_chunks(const_repr):
  # obsolete; look below.
  terminalNodes = re.findall('\([^(]+? [^)]+?\)', const_repr);
  for terminal_repr in terminalNodes:
    needle_idx = const_repr.find(terminal_repr);
    if needle_idx != -1:
      end_idx = needle_idx+len(terminal_repr);
      for ch in const_repr[end_idx:]:
        if ch == ')':
          end_idx += 1
        else:
          break
      yield const_repr[:end_idx].replace(terminal_repr, '*').replace(' ', '_');
      const_repr = const_repr[end_idx:].strip();

def constparse_chunks(const_repr):
  quote, paren = False, False;
  terminalIndices = [];
  start_idx, end_idx = 0, 0;
  for idx, ch in enumerate(const_repr):
    if ch == '(':
      if not quote:
        start_idx = idx;
        paren = True;
    elif ch == ')':
      if (not quote) and paren:
        end_idx = idx+1;
        terminalIndices.append( (start_idx, end_idx) );
        paren = False;
    elif ch == '"':
      quote = not quote;
  cur_idx = 0;
  for terminalIdx in terminalIndices:
    start_idx, end_idx = terminalIdx;
    terminal_repr = const_repr[start_idx:end_idx];
    for ch in const_repr[end_idx:]:
      if ch == ')':
        end_idx += 1;
      else:
        break;
    yield const_repr[cur_idx:end_idx].replace(terminal_repr, '*').strip().replace(' ', '_');
    cur_idx = end_idx;

def augment_constparse(depparsesList, constparsesList):
  global AUG_CONLL07_COLUMNS, FIELDS;
  #FIELDS = AUG_CONLL07_COLUMNS;
  new_buf = [];
  def worker(deptree, consttree):
    for depedge, constchunk in zip(deptree, constparse_chunks(constree)):
      depedge['feats'] = constchunk;
  sentences_to_conll(stdout, starmap(worker, izip(depparsesList, constparsesList)));

def makeConstituencyTree(conll_sentences):
  for conll_sent in conll_sentences:
    yield ' '.join(edge['feats'].replace('_', ' ').replace('*', '(%s %s)'%(edge['postag'], edge['form'])) for edge in conll_sent);
  return;

def addWNCategories(mapping, conll_sentences):
  for conll_sent in conll_sentences:
    yield [dict(edge.items()+\
        [('cpostag', mapping.get(edge['postag'], 'f')), \
         ('lemma', edge['lemma'] if edge['lemma'] != '<unknown>' else edge['form'])]) \
         for edge in conll_sent];

if __name__ == '__main__':
  import cProfile, pstats, sys;   
  '''
  try:
    cProfile.run("sentences_to_tok(sys.stdout, sentences_from_conll(sys.stdin))", "profiler")
    programStats = pstats.Stats("profiler")
    programStats.sort_stats('tottime').print_stats(50)
  except KeyboardInterrupt:
    programStats = pstats.Stats("profiler")
    programStats.sort_stats('tottime').print_stats(50)
    sys.exit(1)
  '''
  #global FIELDS, CONLL07_COLUMNS, CONLL09_COLUMNS;
  inputFilePath  = '' if len(sysargv) < 2 else sysargv[1];
  outputFilePath = '' if len(sysargv) < 3 else sysargv[2];
  FIELDS = CONLL09_COLUMNS;
  #FIELDS = CONLL07_COLUMNS;

  try:
    from mtutils import moses_deescapeseq;
  except ImportError:
    moses_deescapeseq = lambda x: x;

  #augment_constparse(sentences_from_conll(sysargv[1]), random_utils.lines_from_file(sysargv[2]));

  #'''
  with random_utils.smart_open(inputFilePath, 'rb') as inputfile, random_utils.smart_open(outputFilePath, 'wb') as outputfile:
    #sentences_to_tok(outputfile,  sentences_from_conll(inputfile));
    #sentences_to_propercased(outputfile, sentences_from_conll(inputfile));
    #sentences_to_tagged(outputfile, sentences_from_conll(inputfile));
    sentences_to_conll09(outputfile, tokenized_to_sentences(imap(moses_deescapeseq, inputfile)));
    #sentences_to_conll09(outputfile, tagged_to_sentences(inputfile));
    #random_utils.lines_to_file(outputFilePath, makeConstituencyTree(sentences_from_conll(inputfile)));
    #mapping = dict((x.strip(), y.strip()) for x, y in map(lambda x: x.split('\t', 1), (line for line in stdin)));
    #sentences_to_conll07(outputfile, addWNCategories(mapping, sentences_from_conll(inputfile)));
  sys.exit(0);
  #'''
