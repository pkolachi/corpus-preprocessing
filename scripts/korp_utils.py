
import codecs, itertools, multiprocessing, os, os.path, random, re, shlex, subprocess, sys;
from math import log10;
import conll_utils, random_utils;
#import lxml.etree as etree;
import xml.etree.cElementTree as etree;
#import xml.etree.ElementTree as etree;

def getSentencesFromMalformedXML(inputfile):
    sentenceProc, sentence = False, [];
    for line in random_utils.lines_from_file(inputfile):
	if line.startswith('<sentence'):
	    sentenceProc = True;
	    sentence.append(line.strip());
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
	conll_line['form'] = token_node.text.strip() if token_node.text else token_node.attrib['lemma'];
	conll_sentence.append(conll_line);
    return conll_sentence;

def convertKorpXMLtoCoNLL(inputfile, outputfile):
    conll_sentences = [];
    with random_utils.smart_open(outputfile, 'w') as outfile:
	for sentence in getSentencesFromMalformedXML(inputfile):
	    conll_sentences.append( convertSentenceToConLL(sentence.encode('utf-8')) );
	    # memory adjustments
	    if len(conll_sentences) > 10000:
		conll_utils.sentences_to_conll07(outfile, conll_sentences);
		conll_sentences = [];
	if len(conll_sentences):
	    conll_utils.sentences_to_conll07(outfile, conll_sentences);
    return;

def extractSentencesFromKorpXML(inputfile, outputfile):
    tok_sentences = [];
    with random_utils.smart_open(outputfile, 'w') as outfile:
	print >>sys.stderr, inputfile;
	for sentence in getSentencesFromMalformedXML(inputfile):
	    sent_node = etree.fromstring(sentence.encode('utf-8'));
	    tok_sentences.append( " ".join([token_node.text.strip() for token_node in sent_node.findall(".//w")]) );
	    # memory adjustments
	    if len(tok_sentences) > 5000:
		print >>outfile, "\n".join(tok_sentences);
		tok_sentences = [];
	if len(tok_sentences):
	    print >>outfile, "\n",join(tok_sentences);
    return;

if __name__ == '__main__':
    #writeSegmentedCoreNLPOutputIntoDirectory(sys.argv[2:], sys.argv[1]);
    convertKorpXMLtoCoNLL(sys.argv[1], sys.argv[2]);
    #extractSentencesFromKorpXML(sys.argv[1], sys.argv[2]);
