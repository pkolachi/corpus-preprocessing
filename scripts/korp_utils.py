
import codecs, itertools, multiprocessing, os, os.path, random, re, shlex, subprocess, sys;
from math import log10;
import conll_utils;
#import lxml.etree as etree;
import xml.etree.cElementTree as etree;
#import xml.etree.ElementTree as etree;

def getSentencesFromMalformedXML(inputfile):
    with codecs.open(inputfile, 'r', 'utf-8') as infile:
	sentenceProc = False;
	sentence = [];
	for line in infile:
	    if line.startswith('<sentence'):
		sentence.append(line.strip());
		sentenceProc = True;
	    elif sentenceProc == True and line.startswith('</sentence'):
		sentence.append(line.strip());
		sentenceProc = False;
		yield '\n'.join(sentence);
		sentence = [];
	    elif sentenceProc == True:
		sentence.append(line.strip());

def convertSentenceToConLL(sent_xml_repr):
    sent_node = etree.fromstring(sent_xml_repr);
    conll_sentence = [];
    for token_node in sent_node.findall(".//w"):
	conll_line, isNer = {}, False;
	conll_line['id'] = str(int(token_node.attrib['ref']));
	for attr, val in token_node.attrib.iteritems():
	    if attr == 'ref':
		continue;
	    elif attr == 'pos' and val.strip() != '':
		conll_line['postag'] = val.strip();
	    elif attr == 'lemma' and val.strip(' |') != '':
		conll_line['lemma'] = '|'.join([re.sub('\s+', '_', l) for l in val.strip(' |').split('|')]);
	    elif attr == 'dephead':
		conll_line['head'] = str(int(val) if val.strip() != '' else 0);
	    elif attr == 'deprel':
		conll_line['deprel'] = val.strip();
	    #elif attr in ['msd', 'lex', 'saldo', 'prefix', 'suffix']:
	    elif attr in ['lex', 'saldo']:
		complex_feat_val = '%'.join([re.sub('\s+', '_', l) for l in val.strip(' |').split('|')]);
		if complex_feat_val.strip() != '':
		    conll_line.setdefault('feats', {})[attr] = complex_feat_val;
	conll_line['form'] = token_node.text.strip();
	conll_sentence.append(conll_line);
    return conll_sentence;

def convertKorpXMLtoCoNLL(inputfile, outputfile):
    conll_sentences = [];
    with codecs.open(outputfile, 'w', 'utf-8') as outfile:
	print >>sys.stderr, inputfile;
	for sentence in getSentencesFromMalformedXML(inputfile):
	    conll_sentences.append( convertSentenceToConLL(sentence.encode('utf-8')) );
	    # memory adjustments
	    if not len(conll_sentences)%10000:
		conll_utils.sentences_to_conll07(outfile, conll_sentences);
		conll_sentences = [];
	if len(conll_sentences) != 0:
	    conll_utils.sentences_to_conll07(outfile, conll_sentences);
    return;

def extractSentencesFromKorpXML(inputfile, outputfile):
    tok_sentences = [];
    with codecs.open(outputfile, 'w', 'utf-8') as outfile:
	print >>sys.stderr, inputfile;
	for sentence in getSentencesFromMalformedXML(inputfile):
	    sent_node = etree.fromstring(sentence.encode('utf-8'));
	    tok_sentences.append( " ".join([token_node.text.strip() for token_node in sent_node.findall(".//w")]) );
	    # memory adjustments
	    if not len(tok_sentences)%10000:
		for sent in tok_sentences:
		    print >>outfile, sent.strip();
		tok_sentences = [];
	if len(tok_sentences) != 0:
	    for sent in tok_sentences:
		print >>outfile, sent.strip();
    return;

if __name__ == '__main__':
    #writeSegmentedCoreNLPOutputIntoDirectory(sys.argv[2:], sys.argv[1]);
    convertKorpXMLtoCoNLL(sys.argv[1], sys.argv[2]);
    #extractSentencesFromKorpXML(sys.argv[1], sys.argv[2]);
