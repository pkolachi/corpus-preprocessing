#!/usr/bin/env python

from __future__ import print_function, division;
try:
  from globalimports import *;
  from random_utils import llnum2name as llnum2name;
  import random_utils;
except ImportError:
  sys.exit(1);
  llnum2name = lambda x: str(x);

from itertools import dropwhile, takewhile;
import re;

# this allows to switch the module with any other module
# for e.g. memopt_conll_utils or a faster cython version
fast_conll = __import__('conll_utils');

global CONLL07_COLUMNS, CONLL09_COLUMNS, FIELDS;

# These are the labels on the columns in the CoNLL 2007 dataset.
CONLL07_COLUMNS = ('id', 'form', 'lemma', \
    'cpostag', 'postag', 'feats', \
    'head', 'deprel', \
    'phead', 'pdeprel', );
# These are the labels on the columns when constituency parser out is
# converted to dependency format
AUG_CONLL07_COLUMNS = ('id', 'form', 'lemma', \
    'cpostag', 'postag', 'const_parse', 'feats', \
    'head', 'deprel', \
    'phead', 'pdeprel', );
# These are the labels on the columns in the CoNLL 2009 dataset.
CONLL09_COLUMNS = ('id', 'form', 'lemma', 'plemma', \
    'postag', 'ppostag', 'feats', 'pfeats', \
    'head', 'phead', 'deprel', 'pdeprel', 'fillpred', 'sense', );
# These are the labels on the columns in the ConllU format (UD treebanks).
CONLLU_COLUMNS = ('id', 'form', 'lemma', \
    'cpostag', 'postag', 'feats', \
    'head', 'deprel', \
    'deps', 'misc', );

# These are the labels on the columns when Berkeley parser 
# is given pre-tagged input
BERKELEY_COLUMNS = ('form', 'cpostag', );
# These are the labels on the output of morfette tagger
MORFETTE_COLUMNS = ('form', 'lemma', 'postag', );

FIELDS = CONLLU_COLUMNS;
BUF_SIZE = 100000;

def words_from_conll(lines, fields):
  '''Read words for a single sentence from a CoNLL text file.'''
  # using this with filter doubles parsing time 
  isNotEmpty  = lambda (f, v): v != '_'; 
  isMultiWord = lambda x: re.match('^[0-9]+?-[0-9]+?$', x);
  parseFeats  = lambda fstruc: tuple(tuple(x.split('=', 1)) for x in fstruc.split('|'));
  for line in lines:
    entries = line.split('\t');
    if fields == CONLLU_COLUMNS and isMultiWord(entries[0]):
      continue;
    entries = zip(fields, entries);
    # entries = ((x, y) for x, y in entries if y != '_'); 
    #-- there doesn't to be any point in have this?
    entry = defaultdict(lambda: '_', entries);
    if 'feats' in fields and entry['feats'] != '_':
      entry['feats'] = parseFeats(entry['feats']);
    if 'pfeats' in fields and entry['pfeats'] != '_':
      entry['feats'] = parseFeats(entry['feats']);
    yield entry;

def lines_from_conll__(lines, comments=False):
  '''Read lines for a single sentence from a CoNLL text file.'''
  sel_lines = list(takewhile(lambda X: X.strip(), lines));
  return sel_lines[1:] if comments and sel_lines[0].startswith('#') \
      else sel_lines;

def lines_from_conll(lines):
  '''Read lines for a single sentence from a CoNLL text file.'''
  for line in lines:
    if not line.strip():
      return;
    yield line.strip();

def sentences_from_conll(stream, comments=True):
  '''Read sentences from lines in an open CoNLL file handle.'''
  global FIELDS;
  sent_count = 0;
  while True:
    lines = tuple(lines_from_conll(stream));
    if not len(lines):
      break;
    sent_count += 1;
    if comments:
      comm_lines = takewhile(lambda X: X.startswith('#'), lines);
      comm_lines = '\n'.join(comm_lines); 
    conll_lines = dropwhile(lambda X: X.startswith('#'), lines);
    tree = list(fast_conll.words_from_conll(conll_lines, fields=FIELDS));
    if len(comm_lines) and comments:
      # we are deliberately dropping all comment lines;
      yield tree;#(comm_lines, tree);
    else:
      yield tree;
    if not sent_count%BUF_SIZE:
      print("(CoNLL:%s)" %(llnum2name(sent_count)), file=stderr, end=' ');
  print("(CoNLL:%s)" %(llnum2name(sent_count)), file=stderr);

def words_to_conll(sent, fields=CONLL07_COLUMNS):
  str_repr = [];
  if type(sent) == type(()) and len(sent) == 2:
    str_repr.append(str(sent[0]));
    sent = sent[1];
  for token in sent:
    feat_repr = '|'.join('%s=%s' %(feat, value) \
        for feat, value in token['feats']) \
        if 'feats' in token and type(token['feats']) == type(()) \
        else token['feats'];
    token['feats'] = feat_repr if feat_repr.strip() else '_';
    str_repr.append('\t'.join(token[feat] for feat in fields));
  return '\n'.join(str_repr);

def sentences_to_conll07(handle, sentences):
  global CONLL07_COLUMNS;
  if not sentences:
    print("(CoNLL07:%s)" %(llnum2name(0)), file=stderr);
    return;
  step_size = 0;
  while True:
    buf_sents = islice(sentences, BUF_SIZE);
    for sent_count, sent in enumerate(buf_sents, start=1):
      print(fast_conll.words_to_conll(sent, fields=CONLL07_COLUMNS), file=handle);
      print("", file=handle);
    print("(CoNLL07:%s)" %(llnum2name(sent_count+step_size*BUF_SIZE)), \
        file=stdout, end=' ');
    if sent_count < BUF_SIZE:
      break;
    step_size += 1;
  return;

def sentences_to_conll09(handle, sentences):
  global CONLL09_COLUMNS;
  if not sentences:
    print("(CoNLL09:%s)" %(llnum2name(0)), file=stderr);
    return;
  step_size = 0;
  while True:
    buf_sents = islice(sentences, BUF_SIZE);
    for sent_count, sent in enumerate(buf_sents, start=1):
      print(fast_conll.words_to_conll(sent, fields=CONLL09_COLUMNS), file=handle);
      print("", file=handle);
    print("(CoNLL07:%s)" %(llnum2name(sent_count+step_size*BUF_SIZE)), \
        file=stdout, end=' ');
    if sent_count < BUF_SIZE:
      break;
    step_size += 1;
  return;

def sentences_to_conll(handle, sentences):
  global FIELDS;
  if not sentences:
    print("(CoNLL09:%s)" %(llnum2name(0)), file=stderr);
    return;
  step_size = 0;
  while True:
    buf_sents = islice(sentences, BUF_SIZE);
    for sent_count, sent in enumerate(buf_sents, start=1):
      print(fast_conll.words_to_conll(sent, fields=FIELDS), file=handle);
      print("", file=handle);
    print("(CoNLL07:%s)" %(llnum2name(sent_count+step_size*BUF_SIZE)), \
        file=stderr, end=' ');
    if sent_count < BUF_SIZE:
      break;
    step_size += 1;
  return;

def sentences_to_tok(handle, sentences):
  for sent_idx, sent in enumerate(sentences, start=1):
    try:
      print(" ".join([token['form'] for token in sent]), file=handle);
    except TypeError:
      print(repr(sent), file=stderr);
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
    print('%s%s' %(repr(sentinfo)+'\t' if metaInfo else '', \
        " ".join(['%s%c%s'%(token['form'], delim, token['postag']) \
        for token in sent])), file=handle);
  return;

def tokenized_to_sentences(sentences):
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
    for depedge, constchunk in zip(deptree, constparse_chunks(consttree)):
      depedge['feats'] = constchunk;
    return deptree;
  sentences_to_conll(stdout, starmap(worker, zip(depparsesList, constparsesList)));

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
  #global FIELDS, CONLL07_COLUMNS, CONLL09_COLUMNS;
  #import cProfile, pstats, sys;   
  #global fast_conll;
  #fast_conll = __import__('memopt_conll_utils');
  '''
  try:
    #cProfile.run("sentences_to_tok(sys.stderr, sentences_from_conll(sys.stdin))", "profiler")
    cProfile.run("fast_conll.sentences_to_conll07(sys.stderr, fast_conll.sentences_from_conll(sys.stdin))", "profiler")
    programStats = pstats.Stats("profiler")
    programStats.sort_stats('tottime').print_stats()
  except KeyboardInterrupt:
    programStats = pstats.Stats("profiler")
    programStats.sort_stats('tottime').print_stats()
    sys.exit(1)
  
  '''
  inputFilePath  = '' if len(sysargv) < 2 else sysargv[1];
  outputFilePath = '' if len(sysargv) < 3 else sysargv[2];
  if inputFilePath and outputFilePath:
    print("Warning: When using bz2 files as input/output, its faster to use bash and redirect from stdin/stdout over using Python Bz2 library", file=stderr);
  
  #FIELDS = CONLL09_COLUMNS;
  FIELDS = CONLL07_COLUMNS;

  try:
    from mtutils import moses_deescapeseq;
  except ImportError:
    moses_deescapeseq = lambda x: x;

  #augment_constparse(sentences_from_conll(sysargv[1]), random_utils.lines_from_file(sysargv[2]));

  with random_utils.smart_open(inputFilePath, 'rb') as inputfile, random_utils.smart_open(outputFilePath, 'wb') as outputfile:
    sentences_to_tok(outputfile,  sentences_from_conll(inputfile));
    #sentences_to_propercased(outputfile, sentences_from_conll(inputfile));
    #sentences_to_tagged(outputfile, sentences_from_conll(inputfile));
    #sentences_to_conll09(outputfile, tokenized_to_sentences(map(moses_deescapeseq, inputfile)));
    #sentences_to_conll09(outputfile, tagged_to_sentences(inputfile));
    #random_utils.lines_to_file(outputFilePath, makeConstituencyTree(sentences_from_conll(inputfile)));
    #mapping = dict((x.strip(), y.strip()) for x, y in map(lambda x: x.split('\t', 1), (line for line in stdin)));
    #sentences_to_conll07(outputfile, addWNCategories(mapping, sentences_from_conll(inputfile)));
    #random_utils.lines_to_filehandle(outputfile, makeConstituencyTree(sentences_from_conll(inputfile)));
  sysexit(0);
  #'''
