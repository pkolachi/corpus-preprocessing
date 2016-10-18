
import sys;
import nltk.tree;
from nltk.stem import wordnet;
from globalimports import *;
import conll_utils, random_utils;

#sys.stdout = codecs.getwriter('utf-8')(sys.stdout);

def getTokenizedTreebank(treebankfile):
  for line in random_utils.lines_from_file(treebankfile):
    if line.strip() == 'NONE':
      yield line.strip();
      continue;
    tree = nltk.tree.Tree.fromstring(line.strip());
    #tree = nltk.tree.Tree.parse(line.strip());
    yield ' '.join(tree.leaves());
    
def get_wordnet_category(treebank_tag):
  if treebank_tag.startswith('J'):   return 'a';
  elif treebank_tag.startswith('V'): return 'v';
  elif treebank_tag.startswith('N'): return 'n';
  elif treebank_tag.startswith('R'): return 'r';
  else:                              return None;

def wnLemmatize_tagged(conll_sentence):
  lemmatizer = wordnet.WordNetLemmatizer();
  for token in conll_sentence:
    wn_postag = get_wordnet_category(token['postag']);
    yield (token['form'], lemmatizer.lemmatize(token['form'],\
        wn_postag if wn_postag != None else wordnet.NOUN));
  yield ('', '');

def wnLemmatize_CoNLL(conllfile):
  with random_utils.smart_open(conllfile) as infile:
    for sentence in conll_utils.sentences_from_conll(infile):
      for token, lemma in wnLemmatize_tagged(sentence):
        print '%s\t%s' %(token, lemma);
  return;

def generatePhrases(parseStr):
  tree = nltk.tree.Tree.parse(parseStr.strip());
  for subtree in tree.subtrees():
    if len(subtree.leaves()) <= 6:
      yield (subtree.node, ' '.join(subtree.leaves()));

def leafancestors(parseStr):
  tree = nltk.tree.Tree(parsestr);
  leaf_count = len(tree.leaves());
  for idx in xrange(leaf_count):
    leafpath_idx = tree.leaf_treeposition(idx);
    leafpath = [tree[leafpath_idx[:idx]].node \
        for idx in xrange(1, len(leafpath_idx))];
    yield tuple(leafpath);

def printSyntacticPhrases(treebankfile):
  for line in random_utils.lines_from_file(treebankfile):
    if line.strip() in ['(ROOT ())', '(())']:
      continue;
    print '\n'.join('%s\t%s'%(chunk[0], chunk[1]) \
        for chunk in generatePhrases(line.strip()));

if __name__ == '__main__':
  #wnLemmatize_CoNLL(sys.argv[1]);
  random_utils.lines_to_filehandle(stdout, getTokenizedTreebank(sys.argv[1]));
  #printSyntacticPhrases(sys.argv[1]);
