
from __future__ import print_function
from libc.stdio cimport *
cdef extern from "stdio.h":
  FILE *fdopen(int, const char *)

import codecs, io, itertools, math, os, random, re, sys;

BUF_SIZE = 1000000;

def smart_open(filename='', mode='rb', large=False):
  bufferSize = ((2<<16)+8) if large == True else io.DEFAULT_BUFFER_SIZE; 
  if filename.strip():
    _, ext = os.path.splitext(filename);
    if ext == '.bz2':
      from bz2 import BZ2File;
      cstream = BZ2File(filename, mode, buffering=bufferSize, compresslevel=1);
      return codecs.getreader('utf-8')(cstream) \
          if mode == 'rb' \
          else codecs.getwriter('utf-8')(cstream);
    elif ext == '.gz':
      from gzip import GzipFile;
      cstream = GzipFile(filename, mode, compresslevel=1);
      return codecs.getreader('utf-8')(cstream) \
          if mode == 'rb' \
          else codecs.getwriter('utf-8')(cstream);
    else:
      return codecs.getreader('utf-8')(open(filename, mode, buffering=bufferSize)) \
          if mode in ['rb', 'r'] \
          else codecs.getwriter('utf-8')(open(filename, mode));
  elif filename == '' and mode in ['r', 'rb']:
    return codecs.getreader('utf-8')(sys.stdin);
  elif filename == '' and mode in ['w', 'wb']:
    return codecs.getwriter('utf-8')(sys.stdout);

cdef char* llnum2name(int number):
  num_map = {3: 'K', 6: 'M', 9: 'B', 12: 'T', 15: 'Q', 18: 'Qu', 21: 'S'}
  good_base = 3
  for base in sorted(num_map, reverse=True):
    try:
      if math.log(number, 10) >= base:
        good_base = base;
        break;
    except ValueError:
      print(number, file=sys.stderr);
      sform = '';
  if (number%10**good_base):
    sform = '%.3f%c' %(float(number)/10**good_base, num_map[good_base]);
  else:
    sform = '%d%c' %(number/10**good_base, num_map[good_base]);
  return sform;
      
def lines_from_filehandle(filehandle, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  line_count = 0;
  from itertools import islice;
  step_size = 0;
  while True:
    buf_file = islice(filehandle, batchsize);
    for line_count, line in enumerate(buf_file, start=1):
      yield line.strip();
    print('(%s)'%(llnum2name(line_count+step_size*batchsize)), \
        file=sys.stderr, end=' ');
    if line_count < batchsize:
      break;
    step_size += 1;
  return;

def lines_from_filehandle__(filehandle, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  line_count = 0;
  for line_count, line in enumerate(filehandle, start=1):
    yield line.strip();
    if not (line_count%batchsize):
      print('(%s)'%(llnum2name(line_count)), file=sys.stderr, end=' ');
  print('(%s)'%(llnum2name(line_count)), file=sys.stderr);
  return;

def lines_from_file(filename, large=False, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  line_count = 0;
  from itertools import islice;
  step_size = 0;
  with smart_open(filename, large=large) as infile:
    while True:
      buf_file = islice(infile, batchsize);
      for line_count, line in enumerate(buf_file, start=1):
        yield line.strip();
      print('(%s)'%(llnum2name(line_count+step_size*batchsize)), \
          file=sys.stderr, end=' ');
      if line_count < batchsize:
        break;
      step_size += 1;
  return;

def lines_from_file__(filename, large=False, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  line_count = 0;
  with smart_open(filename, large=large) as infile:
    for line_count, line in enumerate(infile, start=1):
      yield line.strip();
      if not (line_count%batchsize):
        print('(%s)'%(llnum2name(line_count)), file=sys.stderr, end=' ');
    print('(%s)'%(llnum2name(line_count)), file=sys.stderr);
  return;

def lines_to_filehandle(filehandle, lines, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  line_count = 0;
  from itertools import islice;
  step_size = 0;
  while True:
    buf_lines = islice(lines, batchsize);
    for line_count, sent in enumerate(buf_lines, start=1):
      print(sent.strip(), file=filehandle);
    print('(%s)'%(llnum2name(line_count+step_size*batchsize)), \
        file=sys.stderr, end=' ');
    if line_count < batchsize:
      break;
    step_size += 1;
  return True;

def lines_to_filehandle__(filehandle, lines, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  line_count = 0;
  for line_count, sent in enumerate(lines, start=1):
    print(sent.strip(), file=filehandle);
    if not (line_count%batchsize): 
      print('(%s)'%(llnum2name(line_count)), file=sys.stderr, end=' ');
  print('(%s)'%(llnum2name(line_count)), file=sys.stderr);
  return True;

def lines_to_file(filename, lines, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  line_count = 0;
  from itertools import islice;
  step_size = 0;
  with smart_open(filename, mode='wb') as outfile:
    while True:
      buf_lines = islice(lines, batchsize);
      for line_count, sent in enumerate(buf_lines, start=1):
        print(sent.strip(), file=outfile);
      print('(%s)'%(llnum2name(line_count+step_size*batchsize)), \
          file=sys.stderr, end=' ');
      if line_count < batchsize:
        break;
      step_size += 1;
  return True;

def lines_to_file__(filename, lines, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  line_count = 0;
  with smart_open(filename, mode='wb') as outfile:
    for line_count, sent in enumerate(lines, start=1):
      print(sent.strip(), file=outfile);
      if not (line_count%batchsize): 
        print('(%s)'%(llnum2name(line_count)), file=sys.stderr, end=' ');
    print('(%s)'%(llnum2name(line_count)), file=sys.stderr);
  return True;

def encode_sentence(sentence, vocabulary, id_gen=itertools.count(1)):
  enc_repr = [];
  for token in re.split('\s+', sentence.strip()):
    if token in vocabulary:
      enc_repr.append(vocabulary[token]);
    else:
      vocab_idx = next(id_gen);
      vocabulary[token] = vocab_idx;
      enc_repr.append(vocab_idx);
  return tuple(enc_repr);

def rpartition_indices(start_index, end_index):
  while True:
    if end_index <= start_index:
      return;
    window_size = random.randint(0, end_index-start_index);
    if float(window_size)/(end_index-start_index) < 0.01 or window_size > 7000:
      continue;
    yield start_index, start_index+window_size+1;
    start_index += window_size+1;

def epartition_indices(start_index, end_index, batchSize=5000):
  while True:
    if end_index < start_index:
      return;
    if start_index+batchSize >= end_index:
      yield start_index, end_index;
    else:
      yield start_index, start_index+batchSize;
    start_index += batchSize;

def splitTextFileIntoChunks(filename, outfileprefix=None):
  sentences = [];
  for line in lines_from_file(filename):
    sentences.append( line.strip() );
  folded_sentences = [];
  for foldrange in epartition_indices(0, len(sentences)):
    folded_sentences.append( sentences[foldrange[0]:foldrange[1]] );
  foldcount = len(folded_sentences);
  if outfileprefix:
    pid = os.getpid();
    for foldidx in xrange(foldcount):
      if not lines_to_file('%s.%s.%d'%(outfileprefix, pid, foldidx+1), \
          folded_sentences[foldidx]):
        return False;
      return True;
  else:
    return folded_sentences;

def splitTextFileIntoSizedChunks(filename, outfileprefix=None, maxsize=5000):
  outfileprefix = outfileprefix if outfileprefix else repr(os.getpid());
  line_count, buf, foldidx = 0, [], 1;
  for line in lines_from_file(filename):
    line_count += 1;
    buf.append(line.strip());
    if not line_count%maxsize:
      lines_to_file('%s.%d' %(outfileprefix, foldidx), buf);
      buf = [];
      foldidx += 1;
  if len(buf):
    lines_to_file('%s.%d' %(outfileprefix, foldidx), buf);
  return True;

def filter_items(listitems, selected_ids={}):
  for idx, item in enumerate(listitems, start=1):
    if idx in selected_ids:
      yield item;

