#!/usr/bin/env python

from globalimports import * ;
import random_utils  as ru  ;
import conll_utils   as cu  ;
from itertools import chain, imap as map ;

THR = 100;
words_in_vocab = ru.lines_from_file(sysargv[1]);
words_in_vocab = map(lambda X: X.split(), words_in_vocab);
words_in_vocab = ((entry[0], int(entry[1])) for entry in words_in_vocab);
#words_in_vocab = ifilter(lambda (word, freq): freq >= THR, words_in_vocab);
words_in_vocab = dict(words_in_vocab);

delim = '_';

reformat_conll = lambda sent: [('*root*', '*root*', -1, 'rroot')] + \
    [(edge['form'].lower(), edge['cpostag'], int(edge['head']), edge['deprel']) \
    for edge in sent];

reformat_conll = lambda sent: [('*root*', '*root*', -1, 'rroot')] + \
    [(edge['form'].lower(), edge['cpostag'], int(edge['head']), edge['deprel'].split(':', 1)[0]) \
    for edge in sent];

#linearize      = lambda edge: edge[0] \
#    if edge[1] not in ['ADP', 'AUX', 'CONJ', 'DET', 'NUM', 'PART', 'PRON', 'SCONJ'] \
#    else edge[1];

linearize      = lambda edge: edge[0];

#extract_deps   = lambda sent: \
#    list(chain.from_iterable(izip(\
#    [(sent[edge[2]][0], '%s%c%s' %(edge[3], delim, linearize(edge))) \
#    for edge in sent[1:] if sent[edge[2]][0] in words_in_vocab and edge[0] in words_in_vocab], \
#    [(edge[0], '%sI%c%s' %(edge[3], delim, linearize(sent[edge[2]]))) \
#    for edge in sent[1:] if edge[0] in words_in_vocab and sent[edge[2]][0] in words_in_vocab]\
#    )));

extract_deps   = lambda sent: \
    list(chain.from_iterable(izip(\
    \
    [(sent[edge[2]][0], '%s%c%s' %(edge[3], delim, linearize(edge))) \
    for edge in sent[1:] if sent[edge[2]][0] in words_in_vocab], \
    \
    [(edge[0], '%sI%c%s' %(edge[3], delim, linearize(sent[edge[2]]))) \
    for edge in sent[1:] if edge[0] in words_in_vocab]\
    )));

with ru.smart_open('') as infile:
  conll_sentences = cu.sentences_from_conll(infile);
  conll_sentences = map(reformat_conll, conll_sentences);
  word_contexts   = map(extract_deps, conll_sentences);
  word_contexts   = chain.from_iterable(word_contexts);
  word_contexts   = ("%s %s" %(word, context) for (word, context) in word_contexts);

  ru.lines_to_file('', word_contexts);

