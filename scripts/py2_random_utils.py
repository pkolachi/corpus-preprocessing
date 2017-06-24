#!/usr/bin/env python2

from __future__  import print_function;
from builtins    import xrange    as range;
from bz2         import BZ2File;
from gzip        import GzipFile;
from itertools   import count as counter, \
  islice;
from math        import log10;
from sys         import argv as sysargv, \
  stdin  as stdin, \
  stdout as stdout, \
  stderr as stderr, \
  exit   as sysexit;
import io;
import itertools as it;
import os;
import random;
import re;
import subprocess;

BUF_SIZE = 1000000;

def smart_open(filename='', mode='rb', large=False, fast=False):
  bufferSize = ((2<<16)+8) if large == True else io.DEFAULT_BUFFER_SIZE;
  filename = filename.strip();
  if filename:
    _, ext = os.path.splitext(filename);
    if ext in ('.bz2', '.gz') and mode in ('r', 'rb') and fast:
      cmd = '/usr/bin/bzcat' if ext == '.bz2' else '/usr/bin/gzcat';
      proc = subprocess.Popen([cmd, filename], stdout=subprocess.PIPE);
      iostream = proc.stdout;
      iostream.read1 = iostream.read; ## hack to get BufferedReader to work
    elif ext == '.bz2':
      iostream = BZ2File (filename,  mode=mode, buffering=bufferSize);
    elif ext == '.gz':
      iostream = GzipFile(filename,  mode=mode);
    else:
      iostream = io.open (filename,  mode=mode, buffering=bufferSize);
  else:
    iostream = sysin if mode in ['r', 'rb'] else sysout;
  #-- does not work with python2, only with python3 (3.3 and later)
  #return io.BufferedReader(iostream) if filename.strip() and mode in ['r', 'rb'] \
  #  else io.BufferedWriter(iostream) if filename.strip() and mode in ['w', 'wb'] \
  #  else iostream;  # stdin and stdout cannot be used with BufferedReader/Writer

  # HACK- to use Buffered* for everything other than bz2 in python2 & stdin/stdout;
  return iostream \
    if (filename and ext == '.bz2' and not PY3) or (not filename) \
    else io.BufferedReader(iostream) if mode in ['r', 'rb'] \
    else io.BufferedWriter(iostream);

def llnum2name(number):
  num_map = [
    (21, 'S'),   # sextillion
    (18, 'Qu'),  # quintillion
    (15, 'Q'),   # quadrillion
    (12, 'T'),   # trillion
    ( 9, 'B'),   # billion
    ( 6, 'M'),   # million
    ( 3, 'K')    # thousand
    ]
  fbase, fsuffix =  3, 'K';
  for (base, suf) in num_map:
    try:
      if math.log(number, 10) >= base:
        fbase, fsuffix = base, suf;
        break;
    except ValueError:
      print(number, file=sys.stderr);
  fstring = "{:.3f}{}" 
  if (number%10**fbase):
    return '%.3f%c' %(float(number)/10**good_base, num_map[good_base]);
  else:
    return '%d%c' %(number/10**good_base, num_map[good_base]);
      
def lines_from_filehandle(filehandle, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  from itertools import islice;
  step_size = 0;
  while True:
    line_count = 0;
    buf_file = islice(filehandle, batchsize);
    for line_count, line in enumerate(buf_file, start=1):
      yield line.decode('utf-8').strip();
    print('(%s)'%(llnum2name(line_count+step_size*batchsize)), \
        file=sys.stderr, end=' ');
    if line_count < batchsize:
      break;
    step_size += 1;
  return;

def lines_from_file(filename, large=False, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  from itertools import islice;
  step_size = 0;
  with smart_open(filename, large=large) as infile:
    while True:
      line_count = 0;
      buf_file = islice(infile, batchsize);
      for line_count, line in enumerate(buf_file, start=1):
        yield line.decode('utf-8').strip();
      print('(%s)'%(llnum2name(line_count+step_size*batchsize)), \
          file=sys.stderr, end=' ');
      if line_count < batchsize:
        break;
      step_size += 1;
  return;

def lines_to_filehandle(filehandle, lines, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  from itertools import islice;
  step_size = 0;
  while True:
    line_count = 0;
    buf_lines = islice(lines, batchsize);
    for line_count, sent in enumerate(buf_lines, start=1):
      filehandle.write(u"{0}\n".format(sent.strip()).encode('utf-8'));
    print('(%s)'%(llnum2name(line_count+step_size*batchsize)), \
        file=sys.stderr, end=' ');
    if line_count < batchsize:
      break;
    step_size += 1;
  return True;

def lines_to_file(filename, lines, batchsize=0):
  global BUF_SIZE;
  batchsize = BUF_SIZE if not batchsize else batchsize;
  from itertools import islice;
  step_size = 0;
  with smart_open(filename, mode='wb') as outfile:
    while True:
      line_count = 0;
      buf_lines = islice(lines, batchsize);
      for line_count, sent in enumerate(buf_lines, start=1):
        outfile.write(u"{0}\n".format(sent.strip()).encode('utf-8'));
      print('(%s)'%(llnum2name(line_count+step_size*batchsize)), \
          file=sys.stderr, end=' ');
      if line_count < batchsize:
        break;
      step_size += 1;
  return True;

def encode_sentence(sentence, vocabulary, id_gen=counter(1)):
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
    for foldidx in range(foldcount):
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

