
import codecs, sys;
from nltk.stem import wordnet;
import nltk.tree;
import conll_utils;

#sys.stdout = codecs.getwriter('utf-8')(sys.stdout);

def getTokenizedTreebank(treebankfile):
    #with codecs.open(treebankfile, 'r', 'utf-8') as infile:
    with codecs.open(treebankfile, 'r') as infile:
	for line in infile:
	    if line.strip() == 'NONE':
		yield line.strip();
		continue;
	    tree = nltk.tree.Tree.parse(line.strip());
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
	yield (token['form'], lemmatizer.lemmatize(token['form'], wn_postag if wn_postag != None else wordnet.NOUN));
    yield ('', '');

def wnLemmatize_CoNLL(conllfile):
    with codecs.open(conllfile, 'r', 'utf-8') as infile:
	for sentence in conll_utils.sentences_from_conll(infile):
	    for token, lemma in wnLemmatize_tagged(sentence):
		print '%s\t%s' %(token, lemma);
    return;

def generatePhrases(parseStr):
    tree = nltk.tree.Tree.parse(parseStr.strip());
    for subtree in tree.subtrees():
	if len(subtree.leaves()) <= 6:
	    yield (subtree.node, ' '.join(subtree.leaves()));

def printSyntacticPhrases(treebankfile):
    with codecs.open(treebankfile, 'r') as infile:
	count = 0;
	for line in infile:
	    count += 1;
	    #if not count%100000: print >>sys.stderr, ".",
	    if line.strip() in ['(ROOT ())', '(())']:
		continue;
	    for chunk in generatePhrases(line.strip()):
		print "%s\t%s" %(chunk[0], chunk[1]);

if __name__ == '__main__':
    #wnLemmatize_CoNLL(sys.argv[1]);
    for line in getTokenizedTreebank(sys.argv[1]): print line;
    #printSyntacticPhrases(sys.argv[1]);
