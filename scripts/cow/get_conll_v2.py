
from globalimports import *;
import random_utils;
import conll_utils;
import re;

def parse_attributes(attr_str):
  attr_str = attr_str.strip().split();
  for attr in attr_str:
    if attr.startswith('docid') or attr.startswith('id'):
      docid = attr;
    elif attr.startswith('bdc'):
      bdc = attr;
    elif attr.startswith('bpc'):
      bpc = attr;
  return '%s,%s,%s' %(docid, bdc, bpc);

def sentences_from_xmlfile(filename):
  sent = [];
  for line in random_utils.lines_from_file(filename):
    if line.startswith('<s '):
      # find the comment; but initialize sent first;
      sent = [];
      comment = parse_attributes(line[2:-1]);
    elif line == '</s>':
      yield (comment, sent);
    else:
      #word, postag, lemma = re.split('\s+', line.strip());
      word, lemma, postag = re.split('\s+', line.strip());  # seems to be the case with es
      sent.append((word, postag, lemma));

def fields2conll(sent):
  #return (sent[0], [{'id': str(idx), 'form': wordentry[0], 'lemma': wordentry[2], 'postag': wordentry[1]} for idx, wordentry in enumerate(sent[1], start=1)]);
  return [{'id': str(idx), 'form': wordentry[0], 'lemma': wordentry[2], 'postag': wordentry[1]} for idx, wordentry in enumerate(sent[1], start=1)];

def prepare_mate(sent):
  return [{'id': edge['id'], 'form': edge['form'], 'plemma': edge['lemma']} for edge in sent[1]];

MAX_PART_SIZE = 1000000;
SMALL_BUF_SIZE = MAX_PART_SIZE/4;

mate_outconllprefix = sysargv[1].replace('.xml.gz', '');
mate_outconllprefix = mate_outconllprefix.replace('01', '');
partids = 1;
mate_outconllfilename = '%s_part%s.mateinput.conll09.bz2' %(mate_outconllprefix, str(partids).zfill(4));
mate_outconll = random_utils.smart_open(mate_outconllfilename, 'wb');
PART_BUF = [];
cur_sentences_count = 0;

with random_utils.smart_open('%s.clean.lines-retained.bz2' %(mate_outconllprefix), 'wb') as idsfile:
  for origfilename in sysargv[1:]:
    conlloutfilename = origfilename.replace('.xml', '.conll');
    if conlloutfilename.endswith('.gz'):
      conlloutfilename = conlloutfilename.replace('.gz', '.bz2');
    with random_utils.smart_open(conlloutfilename, 'wb') as localoutfile:
      original_sentences = sentences_from_xmlfile(origfilename);
      conll_sentences    = imap(fields2conll, original_sentences);
      while True:
        buf_conll_sentences = islice(conll_sentences, SMALL_BUF_SIZE);
        buf_conll_sentences = list(buf_conll_sentences);
        # first write out this buf to local output file;
        conll_utils.sentences_to_conll07(localoutfile, buf_conll_sentences);

        '''
        sent_ids       = (X[0] for X in buf_conll_sentences if len(X[1]) < 100);
        random_utils.lines_to_filehandle(idsfile, sent_ids);
        mate_sentences = imap(prepare_mate, buf_conll_sentences); 
        filtered_sents = [X    for X in mate_sentences if len(X) < 100];

        if cur_sentences_count + len(PART_BUF) + len(filtered_sents) <= MAX_PART_SIZE:
          if PART_BUF:
            conll_utils.sentences_to_conll09(mate_outconll, imap(prepare_mate, PART_BUF));
            PART_BUF = [];
            cur_sentences_count += len(PART_BUF);
          conll_utils.sentences_to_conll09(mate_outconll, filtered_sents);
          cur_sentences_count += len(filtered_sentences);
          continue;

        if cur_sentences_count + len(PART_BUF) <= MAX_PART_SIZE:
          if PART_BUF:
            conll_utils.sentences_to_conll09(mate_outconll, imap(prepare_mate, PART_BUF));
            PART_BUF = [];
            cur_sentences_count += len(PART_BUF);
          continue;


        else:
          if cur_sentences_count + len(PART_BUF) <= MAX_PART_SIZE:
            conll_utils.sentences_to_conll09(mate_outconll, imap(prepare_mate, PART_BUF));
            PART_BUF = ;
            cur_sentences_count += len(PART_BUF);
        '''

        '''
        random_utils.lines_to_filehandle(idsfile, (X[0] for X in buf_conll_sentences if len(X[1]) < 100));
        PART_BUF.extend(imap(prepare_mate, ifilter(lambda X: len(X[1]) < 100, buf_conll_sentences)));
        if len(PART_BUF) > MAX_PART_SIZE:
          conll_utils.sentences_to_conll09(mate_outconll, PART_BUF[:MAX_PART_SIZE]);
          mate_outconll.close();
          PART_BUF = PART_BUF[MAX_PART_SIZE:];
          partids += 1;
          mate_outconllfilename = '%s_part%s.mateinput.conll09.bz2' %(mate_outconllprefix, str(partids).zfill(4));
          mate_outconll = random_utils.smart_open(mate_outconllfilename, 'wb');'''
        if len(buf_conll_sentences) < SMALL_BUF_SIZE:
          break;
'''
if len(PART_BUF):
  conll_utils.sentences_to_conll09(mate_outconll, PART_BUF);'''

