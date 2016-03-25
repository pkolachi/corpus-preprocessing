
from __future__ import print_function
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

def llnum2name(number):
  num_map = {3: 'K', 6: 'M', 9: 'B', 12: 'T', 15: 'Q', 18: 'Qu', 21: 'S'};
  good_base = 3;
  for base in sorted(num_map, reverse=True):
    try:
      if math.log(number, 10) >= base:
        good_base = base;
        break;
    except ValueError:
      print(number, file=sys.stderr);
  if (number%10**good_base):
    return '%.3f%c' %(float(number)/10**good_base, num_map[good_base]);
  else:
    return '%d%c' %(number/10**good_base, num_map[good_base]);
      
def lines_from_filehandle(filehandle):
  global BUF_SIZE;
  line_count = 0;
  from itertools import islice;
  step_size = 0;
  while True:
    buf_file = islice(filehandle, BUF_SIZE);
    for line_count, line in enumerate(buf_file, start=1):
      yield line.strip();
    print('(%s)'%(llnum2name(line_count+step_size*BUF_SIZE)), file=sys.stderr, end=' ');
    if line_count < BUF_SIZE:
      break;
    step_size += 1;
  return;

def lines_from_filehandle__(filehandle):
  global BUF_SIZE;
  line_count = 0;
  for line_count, line in enumerate(filehandle, start=1):
    yield line.strip();
    if not (line_count%BUF_SIZE):
      print('(%s)'%(llnum2name(line_count)), file=sys.stderr, end=' ');
  print('(%s)'%(llnum2name(line_count)), file=sys.stderr);
  return;

def lines_from_file(filename, large=False):
  global BUF_SIZE;
  line_count = 0;
  from itertools import islice;
  step_size = 0;
  with smart_open(filename, large=large) as infile:
    while True:
      buf_file = islice(infile, BUF_SIZE);
      for line_count, line in enumerate(buf_file, start=1):
        yield line.strip();
      print('(%s)'%(llnum2name(line_count+step_size*BUF_SIZE)), file=sys.stderr, end=' ');
      if line_count < BUF_SIZE:
        break;
      step_size += 1;
  return;

def lines_from_file__(filename, large=False):
  global BUF_SIZE;
  line_count = 0;
  with smart_open(filename, large=large) as infile:
    for line_count, line in enumerate(infile, start=1):
      yield line.strip();
      if not (line_count%BUF_SIZE):
        print('(%s)'%(llnum2name(line_count)), file=sys.stderr, end=' ');
    print('(%s)'%(llnum2name(line_count)), file=sys.stderr);
  return;

def lines_to_filehandle(filehandle, lines):
  global BUF_SIZE;
  line_count = 0;
  from itertools import islice;
  step_size = 0;
  while True:
    buf_lines = islice(lines, BUF_SIZE);
    for line_count, sent in enumerate(buf_lines, start=1):
      print(sent.strip(), file=filehandle);
    print('(%s)'%(llnum2name(line_count+step_size*BUF_SIZE)), file=sys.stderr, end=' ');
    if line_count < BUF_SIZE:
      break;
    step_size += 1;
  return True;

def lines_to_filehandle__(filehandle, lines):
  global BUF_SIZE;
  line_count = 0;
  for line_count, sent in enumerate(lines, start=1):
    print(sent.strip(), file=filehandle);
    if not (line_count%BUF_SIZE): 
      print('(%s)'%(llnum2name(line_count)), file=sys.stderr, end=' ');
  print('(%s)'%(llnum2name(line_count)), file=sys.stderr);
  return True;

def lines_to_file(filename, lines):
  global BUF_SIZE;
  line_count = 0;
  from itertools import islice;
  step_size = 0;
  with smart_open(filename, mode='wb') as outfile:
    while True:
      buf_lines = islice(lines, BUF_SIZE);
      for line_count, sent in enumerate(buf_lines, start=1):
        print(sent.strip(), file=outfile);
      print('(%s)'%(llnum2name(line_count+step_size*BUF_SIZE)), file=sys.stderr, end=' ');
      if line_count < BUF_SIZE:
        break;
      step_size += 1;
  return True;

def lines_to_file__(filename, lines):
  global BUF_SIZE;
  line_count = 0;
  with smart_open(filename, mode='wb') as outfile:
    for line_count, sent in enumerate(lines, start=1):
      print(sent.strip(), file=outfile);
      if not (line_count%BUF_SIZE): 
        print('(%s)'%(llnum2name(line_count)), file=sys.stderr, end=' ');
    print('(%s)'%(llnum2name(line_count)), file=sys.stderr);
  return True;

def encode_sentence(sentence, vocabulary, id_gen=itertools.count(1)):
  enc_repr = [];
  for token in re.split('\s+', sentence.strip()):
    if vocabulary.has_key(token):
      enc_repr.append(vocabulary[token]);
    else:
      vocab_idx = id_gen.next();
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

def filter_iterator(listitems, selected_ids={}):
  for idx, item in enumerate(listitems, start=1):
    if idx in selected_ids:
      yield item;

