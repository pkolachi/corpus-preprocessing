
import codecs, io, itertools, math, os, random, re, string, sys, time;

def smart_open(filename='', mode='rb', large=False):
    bufferSize = ((2<<16)+8) if large == True else io.DEFAULT_BUFFER_SIZE; 
    if filename.strip():
	_, ext = os.path.splitext(filename);
	if ext == '.bz2':
	    from bz2 import BZ2File;
	    return codecs.getreader('utf-8')(BZ2File(filename, mode, buffering=bufferSize))\
		    if mode == 'rb' \
		    else codecs.getwriter('utf-8')(BZ2File(filename, mode));
	elif ext == '.gz':
	    from gzip import GzipFile;
	    return codecs.getreader('utf-8')(GzipFile(filename, mode))\
		    if mode == 'rb' \
		    else codecs.getwriter('utf-8')(GzipFile(filename, mode));
	else:
	    return codecs.getreader('utf-8')(open(filename, mode, buffering=bufferSize)) \
		    if mode == 'rb' \
		    else codecs.getwriter('utf-8')(open(filename, mode));
    elif filename == '' and mode == 'rb':
	return codecs.getreader('utf-8')(sys.stdin);
    elif filename == '' and mode == 'wb':
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
      print >>sys.stderr, number;
  if (number%10**good_base):
    return '%.3f%c' %(float(number)/10**good_base, num_map[good_base]);
  else:
    return '%d%c' %(number/10**good_base, num_map[good_base]);
      
def lines_from_file(filename, large=False):
    bufsize = 1000000;
    with smart_open(filename, large=large) as infile:
	for line_count, line in enumerate(infile):
	    yield line.strip();
	    if not ((line_count+1)%bufsize):
		print >>sys.stderr, '(%s)'%(llnum2name(line_count+1)),
	print >>sys.stderr, '(%s)'%(llnum2name(line_count+1));
    return;

def lines_to_file(filename, lines):
    bufsize = 1000000;
    with smart_open(filename, mode='wb') as outfile:
	for line_count, sent in enumerate(lines):
	    print >>outfile, sent.strip();
	    if not ((line_count+1)%bufsize): 
		print >>sys.stderr, '(%s)'%(llnum2name(line_count+1)),
	print >>sys.stderr, '(%s)'%(llnum2name(line_count+1));
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
	    raise StopIteration;
	window_size = random.randint(0, end_index-start_index);
	if float(window_size)/(end_index-start_index) < 0.01 or window_size > 7000:
	    continue;
	yield start_index, start_index+window_size+1;
	start_index += window_size+1;

def epartition_indices(start_index, end_index, batchSize=5000):
    while True:
	if end_index < start_index:
	    raise StopIteration;
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
