#!/usr/bin/env python

from __future__ import print_function;

from globalimports import *;
import random_utils;
import nltk.util;
import itertools;
from sys import maxint;
from math import log10;

norder = 3;
def estimate_dist(inputfilename):
  char_vcb = {'BOS': True};
  global norder;
  ngramcounts = defaultdict(lambda: 0.0);
  for line in random_utils.lines_from_file(sysargv[1]):
    char_vcb.update(dict((ch, True) for ch in line));
    line = list(line);
    for ngram in nltk.util.ingrams(line, norder, pad_left=True, pad_right=True, pad_symbol='BOS'):
      ngramcounts[ngram] += 1;
  return (char_vcb.keys(), ngramcounts);

def smooth_dist(vocabulary, trigramcounts):
  bigramcounts = defaultdict(lambda: 0.0);
  for key, count in trigramcounts.iteritems():
    bigramcounts[key[:-1]] += count;

  supermin = -maxint+2;
  smoothdistribution = defaultdict(lambda: -10);
  pairs = itertools.combinations(vocabulary, 2);
  for p in pairs:
    bigramcounts[p] += len(vocabulary);
    for ch in vocabulary:
      trigram = (p[0], p[1], ch);
      trigramcounts[trigram] += 1;
      smoothdistribution[''.join(trigram)] = log10(trigramcounts[trigram]/bigramcounts[trigram[:-1]]);

  return smoothdistribution;

def compute_prob(vcbfilename, prob_dist):
  global norder;
  try:
    for fields in imap(lambda X: X.split(), random_utils.lines_from_file(vcbfilename)):
      if len(fields) < 2: 
        continue;
      else:
        word, freq = fields[0], fields[1];
      prob = 0.0;
      word = list(word);
      ngrams = list(nltk.util.ingrams(word, norder, pad_left=True, pad_right=True, pad_symbol='BOS'));
      #print(ngrams, file=stderr);
      for ngram in ngrams:
        prob += prob_dist[ngram];
      prob /= len(ngrams) if len(ngrams) else 1;
      print("%s\t%s\t%f" %(''.join(word), freq, prob));
  except ValueError:
    print(word, file=stderr);
  return;

def main():
  vocab, counts_dist = estimate_dist(sysargv[1]);
  print(len(vocab), file=stderr);
  smooth_prob_dist = smooth_dist(vocab, counts_dist);
  compute_prob(sysargv[2], smooth_prob_dist);
  return;

if __name__ == '__main__':
  main();
