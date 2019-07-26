#!/usr/bin/env python

from __future__ import print_function, division;
try:
  from globalimports import *;
  from random_utils import llnum2name as llnum2name;
  import random_utils;
  import conll_utils;
except ImportError:
  llnum2name = lambda x: str(x);

import re;
import xml.etree.cElementTree as etree;

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
    for attr, val in token_node.attrib.items():
      if attr == 'ref':
        continue;
      elif attr == 'pos' and val.strip() != '':
        conll_line['postag'] = val.strip();
        #conll_line['cpostag'] = val.strip();
      elif attr == 'lemma' and val.strip(' |') != '':
        conll_line['lemma'] = '|'.join([re.sub('\s+', '_', l) \
            for l in val.strip(' |').split('|')]);
      elif attr == 'dephead':
        conll_line['head'] = str(int(val) if val.strip() != '' else 0);
      elif attr == 'deprel':
        conll_line['deprel'] = val.strip();
      elif attr in ['lex', 'saldo']:  #elif attr in ['msd', 'lex', 'saldo', 'prefix', 'suffix']:
        complex_feat_val = '%'.join([re.sub('\s+', '_', l) \
            for l in val.strip(' |').split('|')]);
        if complex_feat_val.strip() != '':
          conll_line.setdefault('feats', {})[attr] = complex_feat_val;
    conll_line['form'] = token_node.text.strip() if token_node.text \
        else token_node.attrib['lemma'];
    conll_sentence.append(conll_line);
  return conll_sentence;

def convertKorpXMLtoCoNLL(inputfile, outputfile):
  def get_sents():
    for sentence in getSentencesFromMalformedXML(inputfile):
      yield convertSentenceToConLL(sentence.encode('utf-8'));
    return;
  with random_utils.smart_open(outputfile, 'wb') as outfile:
    conll_utils.sentences_to_conll07(outfile, get_sents());
  return;

def extractSentencesFromKorpXML(inputfile, outputfile):
  def get_sents():
    for sentence in getSentencesFromMalformedXML(inputfile):
      sent_node = etree.fromstring(sentence.encode('utf-8'));
      yield " ".join([token_node.text.strip() \
          for token_node in sent_node.findall(".//w")]);
    return;
  random_utils.lines_to_file(outputfile, get_sents());
  return;

if __name__ == '__main__':
  convertKorpXMLtoCoNLL(sysargv[1], sysargv[2]);
  #extractSentencesFromKorpXML(sysargv[1], sysargv[2]);
