
from globalimports import *;
import random_utils;

def prepareVcb(corpusfilename):
  outfilename = '%s.snt' %(corpusfilename);
  vocabulary = {'UNK': 1};
  vocab_idgen = counter(2);
  frequencies = defaultdict(lambda: 0);
  with random_utils.smart_open(outfilename, 'w') as outfile:
    for line in random_utils.lines_from_file(corpusfilename):
      encline = random_utils.encode_sentence(line.strip(), vocabulary, vocab_idgen);
      for tokenid in encline:
        frequencies[tokenid] += 1;
      print >>outfile, " ".join(str(tokenid) for tokenid in encline);

    if outfilename != '':
      vcbfilename = '%s.vcb' %(outfilename);
      with random_utils.smart_open(vcbfilename, 'w') as outfile:
        for word, wordidx in sorted(vocabulary.iteritems(), \
            key=itemgetter(1)):
          print >>outfile, "%d %s %d" %(wordidx, word, frequencies[wordidx]);
  return;

def prepareConfusionNetwork(conllfilehandle):
  import itertools;
  mfield = 'lemma';  #mfield = 'form';
  for conll_sent in conllfilehandle:
    factors = [edge[mfield] for edge in conll_sent];
    factorsList = [['%s|%s' %(tok, edge['cpostag']) for tok in token.split('|')] \
        for token, edge in zip(factors, conll_sent)];
    yield map(lambda toks: ' '.join(toks), itertools.product(*factorsList));

def moses_escapeseq(token):
  token = token.replace('&', '&amp;');
  token = token.replace('|', '_PIPE_');
  token = token.replace('<', '&lt;');
  token = token.replace('>', '&gt;');
  token = token.replace("'", '&apos;');
  token = token.replace('"', '&quot;');
  token = token.replace('(', '-lrb-');
  token = token.replace(')', '-rrb-');
  token = token.replace('[', '-lsb-');
  token = token.replace(']', '-rsb-');
  token = token.replace('{', '-lcb-');
  token = token.replace('}', '-rcb-');
  return token;

def moses_deescapeseq(token):
  token = token.replace('&amp;', '&');
  token = token.replace('_PIPE_', '|');
  token = token.replace('&lt;', '<');
  token = token.replace('&gt;', '>');
  token = token.replace('&apos;', "'");
  token = token.replace('&quot;', '"');
  token = token.replace('-lrb-', '(');
  token = token.replace('-rrb-', ')');
  token = token.replace('-LRB-', '(');
  token = token.replace('-RRB-', ')');
  token = token.replace('-lsb-', '[');
  token = token.replace('-rsb-', ']');
  token = token.replace('-LSB-', '[');
  token = token.replace('-RSB-', ']');
  token = token.replace('-lcb-', '{');
  token = token.replace('-rcb-', '}');
  token = token.replace('-LCB-', '{');
  token = token.replace('-RCB-', '}');
  return token;

if __name__ == '__main__':
  import conll_utils;
  import codecs, sys;
  sys.stdout = codecs.getwriter('utf-8')(sys.stdout);
  conll_utils.fields = conll_utils.CONLL07_COLUMNS;
  with random_utils.smart_open(sys.argv[1]) as infile:
    with random_utils.smart_open(sys.argv[2], 'wb') as outfile:
      for hyps in prepareConfusionNetwork(conll_utils.sentences_from_conll(infile)):
        print >>outfile, '\n'.join(hyps);
        print >>outfile, '';
  sys.exit(0);
