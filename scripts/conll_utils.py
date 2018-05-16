#!/usr/bin/env python3

from __future__ import print_function, division;
try:
  import sys;
  assert(sys.version_info > (3, 0, 0));
  PY3 = True;
  from globalimports import *;
  import random_utils as ru;
  llnum2name = ru.llnum2name;
except AssertionError:
  PY3 = False;
  from py2_globalimports import *;
  import py2_random_utils as ru;
  llnum2name = ru.llnum2name;
except ImportError:
  sys.exit(1);
  llnum2name = lambda x: str(x);

import itertools as it;
import re;

# this allows to switch the module with any other module
# for e.g. memopt_conll_utils or a faster cython version
fast_conll = __import__('conll_utils');

# These are the labels on the columns in the CoNLL 2007 dataset.
CONLL07_COLUMNS = (
    'id', 'form', 'lemma',
    'cpostag', 'postag', 'feats',
    'head', 'deprel',
    'phead', 'pdeprel',
    );
# These are the labels on the columns when constituency parser out is
# converted to dependency format
AUG_CONLL07_COLUMNS = (
    'id', 'form', 'lemma',
    'cpostag', 'postag', 'const_parse', 'feats',
    'head', 'deprel',
    'phead', 'pdeprel',
    );
# These are the labels on the columns in the CoNLL 2009 dataset.
CONLL09_COLUMNS = (
    'id', 'form', 'lemma', 'plemma',
    'postag', 'ppostag', 'feats', 'pfeats',
    'head', 'phead', 'deprel', 'pdeprel', 'fillpred', 'sense', 
    );
# These are the labels on the columns in the ConllU format (UD treebanks).
CONLLU_COLUMNS = (
    'id', 'form', 'lemma',
    'postag', 'xpostag', 'feats',
    'head', 'deprel',
    'deps', 'misc', 
    );
AUG_CONLLU_COLUMNS = (
    'id', 'form', 'lemma',
    'postag', 'xpostag', 'const_parse', 'feats',
    'head', 'deprel',
    'deps', 'misc', 
    );

# These are the labels on the columns when Berkeley parser 
# is given pre-tagged input
BERKELEY_COLUMNS = ('form', 'cpostag', );
# These are the labels on the output of morfette tagger
MORFETTE_COLUMNS = ('form', 'lemma', 'postag', );

FIELDS = CONLLU_COLUMNS;
BUF_SIZE = 100000;
TAB_CHAR = re.compile('\t', flags=re.U);

def words_from_conll(lines, fields):
  '''Read words for a single sentence from a CoNLL text file.'''
  # using this with filter doubles parsing time 
  def isMultiWord(x): return re.match('^[0-9]+?-[0-9]+?$', x);
  def parseFeats(fstruc): 
    return tuple(
      tuple(x.split('=', 1)) for x in fstruc.split('|')
    );

  global TAB_CHAR;
  for line in lines:
    entries = re.split(TAB_CHAR, line);
    if fields == CONLLU_COLUMNS and isMultiWord(entries[0]):
      continue;
    entries = zip(fields, entries);
    #-- there doesn't to be any point in have this?
    #entries = ((x, y) for x, y in entries if y != '_'); 
    entry = defaultdict(lambda: u'_', entries);
    '''
    if 'feats' in fields and entry['feats'] != '_':
      entry['feats'] = parseFeats(entry['feats']);
    if 'pfeats' in fields and entry['pfeats'] != '_':
      entry['feats'] = parseFeats(entry['feats']);
    '''
    yield entry;

def lines_from_conll(lines):
  '''Read lines for a single sentence from a CoNLL text file.'''
  for line in lines:
    if not line.strip():
      return;
    yield line.strip();

def sentences_from_conll(stream, comments=True, fields=None):
  '''Read sentences from lines in an open CoNLL file handle.'''
  global FIELDS, BUF_SIZE;
  if not fields: fields = FIELDS;
  sc = 0;
  while True:
    lines = tuple(lines_from_conll(stream));
    if not len(lines):
      break;
    sc += 1;

    if comments:
      comm_lines = it.takewhile(lambda X: X.startswith('#'), lines);
      comm_lines = '\n'.join(comm_lines); 
      conll_lines = it.dropwhile(lambda X: X.startswith('#'), lines);
    else:
      conll_lines = lines;
    
    tree = list(fast_conll.words_from_conll(conll_lines, fields=fields));
    if comments:
      # we are deliberately dropping all comment lines;
      yield (comm_lines, tree);
    else:
      yield tree;
    
    if not sc%BUF_SIZE:
      print("(CoNLL:%s)" %(llnum2name(sc)), file=syserr, end=' ');
  print("(CoNLL:%s)" %(llnum2name(sc)), file=syserr);

def words_to_conll(sent, fields=CONLL07_COLUMNS):
  str_repr = [];
  if type(sent) == type(()) and len(sent) == 2:
    str_repr.append(sent[0]);
    sent = sent[1];
  for token in sent:
    feat_repr = \
        u'|'.join('%s=%s' %(feat, value) for feat, value in token['feats']) \
        if 'feats' in token and type(token['feats']) == type(()) \
        else token['feats'];
    token['feats'] = feat_repr if feat_repr.strip() else '_';
    str_repr.append('\t'.join(token[feat] for feat in fields));
  return u'\n'.join(str_repr);

def sentences_to_conll07(sentences):
  global CONLL07_COLUMNS, BUF_SIZE;
  if not sentences:
    print("(CoNLL07:%s)" %(llnum2name(0)), file=syserr);
    return;
  stepsize = 0;
  while True:
    sc = 0;
    buf_sents = islice(sentences, BUF_SIZE);
    for sc, sent in enumerate(buf_sents, start=1):
      yield fast_conll.words_to_conll(sent, fields=CONLL07_COLUMNS);
      yield "";
    print("(CoNLL07:%s)" %(llnum2name(sc+stepsize*BUF_SIZE)),
        file=syserr, end=' ');
    if sc < BUF_SIZE:
      break;
    stepsize += 1;
  return;

def sentences_to_conll09(sentences):
  global CONLL09_COLUMNS, BUF_SIZE;
  if not sentences:
    print("(CoNLL09:%s)" %(llnum2name(0)), file=syserr);
    return;
  stepsize = 0;
  while True:
    sc = 0;
    buf_sents = islice(sentences, BUF_SIZE);
    for sc, sent in enumerate(buf_sents, start=1):
      yield fast_conll.words_to_conll(sent, fields=CONLL09_COLUMNS);
      yield "";
    print("(CoNLL07:%s)" %(llnum2name(sc+stepsize*BUF_SIZE)),
        file=syserr, end=' ');
    if sc < BUF_SIZE:
      break;
    stepsize += 1;
  return;

def sentences_to_conll(sentences):
  global FIELDS, BUF_SIZE;
  if not sentences:
    print("(CoNLL09:%s)" %(llnum2name(0)), file=syserr);
    return;
  stepsize = 0;
  while True:
    sc = 0;
    buf_sents = islice(sentences, BUF_SIZE);
    for sc, sent in enumerate(buf_sents, start=1):
      yield fast_conll.words_to_conll(sent, fields=FIELDS);
      yield "";
    print("(CoNLL07:%s)" %(llnum2name(sc+stepsize*BUF_SIZE)),
        file=syserr, end=' ');
    if sc < BUF_SIZE:
      break;
    stepsize += 1;
  return;

def sentences_to_tok(sentences):
  for sent_idx, sent in enumerate(sentences, start=1):
    yield " ".join(token['form'] for token in sent);

def sentences_to_tagged(sentences, delim='|'):
  metaInfo = False;
  pos_key = 'ppostag' if FIELDS == CONLL09_COLUMNS \
       else 'postag' if FIELDS == CONLLU_COLUMNS \
       else 'cpostag'; 
  for sent_idx, sent in enumerate(sentences, start=1):
    if type(sent) == type(()) and len(sent) == 2:
      # input is a tuple, with meta-information and actual sentence;
      metaInfo = True;
      sentinfo, sent = sent[0], sent[1];
    tagged_repr = \
        " ".join("{0}{1}{2}".format(token['form'], delim, token[pos_key]) \
          for token in sent);
    yield tagged_repr if not metaInfo \
        else "{0}{1}".format(repr(sentinfo)+'\t', tagged_repr);

def sentences_to_propercased(sentences):
  global FIELDS;
  pos_key = 'ppostag' if FIELDS == CONLL09_COLUMNS \
      else 'postag' if FIELDS == CONLLU_COLUMNS \
      else 'cpostag'; 
  for sent_idx, sent in enumerate(sentences, start=1):
    cased_repr = \
        " ".join(token['form'] if (token['feats'] != '_' and 'nertype' in (f for f, v in token['feats'])) \
              or token[pos_key] == 'PROPN' \
              or token['form'] == 'I' \
          else token['form'].lower() \
        for token in sent);
    yield cased_repr;

def tokenized_to_sentences(sentences):
  global FIELDS;
  for sent_idx, sent in enumerate(sentences, start=1):
    if not sent.strip():
      continue;
    tokens = re.split('\s+', sent.strip());
    if not len(tokens):
      print('warning: empty sentence at %d' %(sent_idx), file=syserr);
      continue;
    conll_sent = [defaultdict(lambda: '_', {'form': tok, 'id': str(tok_idx)})
        for tok_idx, tok in enumerate(tokens, start=1)];
    yield conll_sent;

def tagged_to_sentences(sentences, delim='_'):
  global FIELDS;
  pos_key = 'ppostag' if FIELDS == CONLL09_COLUMNS \
      else 'postag' if FIELDS == CONLLU_COLUMNS \
      else 'cpostag'; 
  for sent_idx, sent in enumerate(sentences, start=1):
    if not sent.strip():
      continue;
    tokens = re.split('\s+', sent.strip());
    if not len(tokens):
      print('warning: empty sentence at %d' %(sent_idx), file=syserr);
      continue;
    tagged_seq = (
      (tok.rsplit(delim, 1)[0], tok.rsplit(delim, 1)[1]) if tok.find(delim) != -1 
      else (tok, 'X')
     for tok in tokens
        );
    conll_sent = [defaultdict(lambda: '_', {'form': tok, 'id': str(tok_idx), pos_key: tag})
        for tok_idx, (tok, tag) in enumerate(tagged_seq, start=1)];
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
  return sentences_to_conll(starmap(worker, zip(depparsesList, constparsesList)));

def makeConstituencyTree(conll_sentences):
  for conll_sent in conll_sentences:
    yield ' '.join(edge['feats'].replace('_', ' ').replace('*', '(%s %s)'%(edge['postag'], edge['form'])) for edge in conll_sent);

def addWNCategories(mapping, conll_sentences):
  for conll_sent in conll_sentences:
    yield [dict(edge.items()
           + [('cpostag', mapping.get(edge['postag'], 'f')), \
              ('lemma', edge['lemma'] if edge['lemma'] != '<unknown>' else edge['form'])]) \
       for edge in conll_sent];

if __name__ == '__main__':
  #global FIELDS, CONLL07_COLUMNS, CONLL09_COLUMNS;
  #import cProfile, pstats, sys;   
  #global fast_conll;
  #fast_conll = __import__('memopt_conll_utils');
  '''
  try:
    #cProfile.run("sentences_to_tok(syserr, sentences_from_conll(sysin))", "profiler")
    cProfile.run("fast_conll.sentences_to_conll07(syserr, fast_conll.sentences_from_conll(sysin))", "profiler")
    programStats = pstats.Stats("profiler")
    programStats.sort_stats('tottime').print_stats()
  except KeyboardInterrupt:
    programStats = pstats.Stats("profiler")
    programStats.sort_stats('tottime').print_stats()
    sys.exit(1)
  
  '''
  inputFilePath  = '' if len(sysargv) < 2 else sysargv[1];
  outputFilePath = '' if len(sysargv) < 3 else sysargv[2];
  if inputFilePath and outputFilePath and (inputFilePath.endswith('bz2') or outputFilePath.endswith('bz2')):
    print("Warning: When using bz2 files as input/output, its faster to use bash and redirect from stdin/stdout over using Python Bz2 library", file=syserr);
  
  #FIELDS = CONLL09_COLUMNS;
  FIELDS = CONLL07_COLUMNS;

  """
  try:
    from mtutils import moses_deescapeseq;
  except ImportError:
    moses_deescapeseq = lambda x: x;
  """

  #augment_constparse(sentences_from_conll(sysargv[1]), ru.lines_from_file(sysargv[2]));

  with ru.smart_open(inputFilePath, 'rb') as inputfile, ru.smart_open(outputFilePath, 'wb') as outputfile:
    inputstream = ru.lines_from_filehandle(inputfile);
    outputcontent = '';

    outputcontent = sentences_to_tok(sentences_from_conll(inputstream));
    #outputcontent = sentences_to_tagged(sentences_from_conll(inputstream));
    #outputcontent = sentences_to_propercased(sentences_from_conll(inputstream));

    #outputcontent = sentences_to_conll07(tagged_to_sentences(inputstream));
    #outputcontent = sentences_to_conll07(tokenized_to_sentences(inputstream));
    #outputcontent = sentences_to_conll09(tagged_to_sentences(inputstream));
    #outputcontent = sentences_to_conll09(tokenized_to_sentences(inputstream));

    #outputcontent = makeConstituencyTree(sentences_from_conll(inputstream));

    #wn_tag_mapping = dict((x.strip(), y.strip()) for x, y in map(lambda x: x.split('\t', 1), (line for line in stdin)));
    #outputcontent = sentences_to_conll07(addWNCategories(mapping, sentences_from_conll(inputstream)));

    ru.lines_to_filehandle(outputfile, outputcontent);
  sysexit(0);
  #'''
