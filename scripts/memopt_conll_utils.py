"""
 An alternate implementation of conll_utils, with additional memory optimizations. 
 The module does not use lazyness, instead it relies on namedtuple to reduce memory
 usage, when the entire CoNLL dataset needs to be loaded
"""

import codecs, os.path, re, sys;
from collections import namedtuple;
try:
    import random_utils;
except ImportError:
    print >>sys.stderr, "Missing necessary module 'random_utils' for module 'conll_utils'";
    sys.exit(1);

# These are the labels on the columns in the CoNLL 2007 dataset.
CONLL07_COLUMNS = ('id', 'form', 'lemma', 'cpostag', 'postag', 'feats', 'head', 'deprel', 'phead', 'pdeprel', )
# These are the labels on the columns in the CoNLL 2009 dataset.
CONLL09_COLUMNS = ('id', 'form', 'lemma', 'plemma', 'postag', 'ppostag', 'feats', 'pfeats', 'head', 'phead', 'deprel', 'pdeprel', 'fillpred', 'sense', )
# These are the labels on the columns in the CoNLL 2009 dataset.
BERKELEY_COLUMNS = ('form', 'cpostag');

fields = CONLL07_COLUMNS;
#fields = BERKELEY_COLUMNS;
CoNLLFields = namedtuple('CoNLLFields', fields);

def words_from_conll(lines, fields):
    '''Read words for a single sentence from a CoNLL text file.'''
    global CoNLLFields
    columnsList = [map(lambda X: X if X != '_' else None, line.split('\t')) for line in lines];
    return tuple(CoNLLFields(*columns) for columns in columnsList);

def lines_from_conll(lines):
    '''Read lines for a single sentence from a CoNLL text file.'''
    for line in lines:
        if not line.strip():
            return;
        yield line.strip();

def sentences_from_conll(handle):
    '''Read sentences from lines in an open CoNLL file handle.'''
    global fields, CoNLLFields;
    CoNLLFields = namedtuple('CoNLLFields', fields);
    sent_count = 0;
    while True:
        lines = tuple(lines_from_conll(handle));
        if not len(lines):
            break;
	sent_count += 1;
	if not sent_count%100000: print >>sys.stderr, "(%s)" %(random_utils.llnum2name(sent_count)),
	yield words_from_conll(lines, fields=fields);
    print >>sys.stderr, "(%s)" %(random_utils.llnum2name(sent_count));

def words_to_conll07(sent, fields):
    global CoNLLFields
    str_repr = [];
    '''
    if type(sent) == type(()) and len(sent) == 2:
	str_repr.append( '#'+str(sent[0]) );
	sent = sent[1];'''
    for token in sent:
	#feat_struct = token.feats;
	#feat_repr = '|'.join(['%s=%s' %(key, feat_struct[key]) for key in sorted(feat_struct.keys())]) if type(feat_struct) == type({}) else '_';
	#token.feats = feat_repr;
	str_repr.append( '\t'.join( map(lambda X: str(X) if X else '_', [getattr(token, feat) for feat in fields]) ) );
    return '\n'.join(str_repr);

def sentences_to_conll07(handle, sentences):
    global fields;
    sent_count = 0;
    for sent in sentences:
	sent_count += 1;
	print >>handle, words_to_conll07(sent, fields=fields);
	print >>handle, "";
	if not sent_count%100000: print >>sys.stderr, "(%s)" %(random_utils.llnum2name(sent_count)),
    print >>sys.stderr, "(%s)" %(random_utils.llnum2name(sent_count));
    return;

def sentences_to_tok(handle, sentences):
    for sent in sentences:
	print >>handle, " ".join([token.form for token in sent]);
    return;

def sentences_to_propercased(handle, sentences):
    for sent in sentences:
	print >>handle, " ".join([token.form.lower() if token.feats.find('nertype') == -1 and token.form != 'I' else token.form for token in sent]);
    return;

def sentences_to_tagged(handle, sentences):
    metaInfo = False;
    delim = '|';
    for sent in sentences:
	if type(sent) == type(()) and len(sent) == 2:
	    # input is a tuple, with meta-information and actual sentence;
	    metaInfo = True;
	    sentidx, sent = sent[0], sent[1];
	print >>handle, '%s%s' %(repr(sentidx)+'\t' if metaInfo else '', " ".join(['%s%c%s'%(token['form'], delim, token['cpostag']) for token in sent]));
    return;

def __constparse_chunks(const_repr):
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

if __name__ == '__main__':
    #sentences_to_conll07(sys.stdout, sentences_from_conll(sys.stdin));
    sentences_to_tok(sys.stdout,  sentences_from_conll(sys.stdin));
    #sentences_to_tagged(sys.stdout,  sentences_from_conll(sys.stdin));
    #sentences_to_propercased(sys.stdout, sentences_from_conll(sys.stdin));
    sys.exit(0);