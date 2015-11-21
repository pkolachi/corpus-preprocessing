
import cProfile, pstats, re, sys;
try:
    from random_utils import llnum2name;
except ImportError:
    llnum2name = lambda x: str(x);

# These are the labels on the columns in the CoNLL 2007 dataset.
CONLL07_COLUMNS = ('id', 'form', 'lemma', 'cpostag', 'postag', 'feats', \
	'head', 'deprel', 'phead', 'pdeprel', )
# These are the labels on the columns in the CoNLL 2009 dataset.
CONLL09_COLUMNS = ('id', 'form', 'lemma', 'plemma', 'postag', 'ppostag', 'feats', \
	'pfeats', 'head', 'phead', 'deprel', 'pdeprel', 'fillpred', 'sense', )
# These are the labels on the columns in the CoNLL 2009 dataset.
BERKELEY_COLUMNS = ('form', 'cpostag');
# These are the labels on the morfette tagger
MORFETTE_COLUMNS = ('form', 'lemma', 'postag');

fields = CONLL07_COLUMNS;
#fields = MORFETTE_COLUMNS;


def words_from_conll(lines, fields):
    '''Read words for a single sentence from a CoNLL text file.'''
    return [dict(zip(fields, line.split('\t'))) for line in lines];

def lines_from_conll(lines, comments=False):
    '''Read lines for a single sentence from a CoNLL text file.'''
    for line in lines:
        if not line.strip():
            return;
	if comments and line.startswith('#'):
	    continue;
        yield line.strip();

def sentences_from_conll(handle, comments=False):
    '''Read sentences from lines in an open CoNLL file handle.'''
    global fields;
    sent_count = 0;
    while True:
        lines = tuple(lines_from_conll(handle, comments));
        if not len(lines):
            break;
        sent_count += 1;
        if not sent_count%100000:
            print >>sys.stderr, "(%s)" %(llnum2name(sent_count)),
        yield words_from_conll(lines, fields=fields);
    print >>sys.stderr, "(%s)" %(llnum2name(sent_count));

def words_to_conll07(sent, fields=CONLL07_COLUMNS):
    str_repr = [];
    if type(sent) == type(()) and len(sent) == 2:
        str_repr.append( '#'+str(sent[0]) );
        sent = sent[1];
    for token in sent:
        feat_repr = '|'.join(['%s=%s' %(key, token['feats'][key]) \
                                   for key in sorted(token['feats'].keys())]) \
                if token.has_key('feats') and type(token['feats']) == type({}) \
                else token.get('feats', '_');
        token['feats'] = feat_repr;
        str_repr.append( '\t'.join([token.get(feat, '_') for feat in fields]) );
    return '\n'.join(str_repr);

def sentences_to_conll07(handle, sentences):
    sent_count = 0;
    for sent in sentences:
        sent_count += 1;
        print >>handle, words_to_conll07(sent);
        print >>handle, "";
        if not sent_count%100000: 
            print >>sys.stderr, "(%s)" %(llnum2name(sent_count)),
    print >>sys.stderr, "(%s)" %(llnum2name(sent_count));
    return;

def sentences_to_conll09(handle, sentences):
    sent_count = 0;
    for sent in sentences:
        sent_count += 1;
        print >>handle, words_to_conll07(sent, fields=CONLL09_COLUMNS);
        print >>handle, "";
        if not sent_count%100000: 
            print >>sys.stderr, "(%s)" %(llnum2name(sent_count)),
    print >>sys.stderr, "(%s)" %(llnum2name(sent_count));
    return;

def sentences_to_conll(handle, sentences):
    global fields;
    sent_count = 0;
    for sent in sentences:
        sent_count += 1;
        print >>handle, words_to_conll07(sent, fields=fields);
        print >>handle, "";
        if not sent_count%100000: 
            print >>sys.stderr, "(%s)" %(llnum2name(sent_count)),
    print >>sys.stderr, "(%s)" %(llnum2name(sent_count));
    return;

def sentences_to_tok(handle, sentences):
    for sent in sentences:
        print >>handle, " ".join([token['form'] for token in sent]);
    return;

def sentences_to_propercased(handle, sentences):
    for sent in sentences:
        print >>handle, " ".join([token['form'].lower() \
                if token['feats'].find('nertype') == -1 and token['form'] != 'I' \
                else token['form'] \
            for token in sent]);
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

def tagged_to_sentences(sentences):
    global fields;
    delim = '_';
    fields = CONLL09_COLUMNS;
    for sent in sentences:
	tokens = re.split('\s+', sent);
	conll_sent = [];
	for idx, tok in enumerate(tokens):
	    try:
		form, pos = tok.rsplit(delim, 1);
	    except ValueError:
		form, pos = tok, 'X';
	    conll_edge = {'form': form, 'id': str(idx+1)};
	    if fields == CONLL09_COLUMNS:
		conll_edge['ppostag'] = pos;
	    elif fields == CONLL07_COLUMNS:
		conll_edge['cpostag'] = pos;
	    elif fields == BERKELEY_COLUMNS:
		conll_edge['cpostag'] = pos;
	    conll_sent.append(conll_edge);
	yield conll_sent;

def prepare_web_version(sentences):
    for sent in sentences:
	for token in sent:
	    if token['cpostag'] == '_' and token['postag'] != '_':
		token['cpostag'] = token['postag'];
	    for field in token.keys():
		if field not in ('id', 'form', 'cpostag'):
		    del token[field];
	yield sent;

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
    import random_utils;  
    '''
    try:
        cProfile.run("sentences_to_tok(sys.stdout, sentences_from_conll(sys.stdin))", "profiler")
        programStats = pstats.Stats("profiler")
        programStats.sort_stats('tottime').print_stats(50)
    except KeyboardInterrupt:
        programStats = pstats.Stats("profiler")
        programStats.sort_stats('tottime').print_stats(50)
        sys.exit(1)'''
    #sentences_to_tok(sys.stdout,  sentences_from_conll(sys.stdin));
    #sentences_to_tagged(sys.stdout,  sentences_from_conll(sys.stdin));
    #with random_utils.smart_open(sys.argv[2], 'wb') as outfile: 
    #	sentences_to_conll09(outfile, tagged_to_sentences(random_utils.lines_from_file(sys.argv[1])));
    #sentences_to_propercased(sys.stdout, sentences_from_conll(sys.stdin));
    sys.exit(0);
