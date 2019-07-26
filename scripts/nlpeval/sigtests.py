#!/usr/bin/env python3

from itertools import groupby;

from globalimports import *;

'''
NOTES:
  The list of significance tests have been picked from
  http://ir.cis.udel.edu/SIGIR14tutorial/slides.pdf

  The implementation i.e. choice of function design is guided by
  http://docs.scipy.org/doc/scipy-0.15.1/reference/stats.html
  This module contains the implementations in Python for many
  of these statistical tests.

  Why then should this module be helpful?
  Its aimed at a low-level understanding of different statistical significance
  tests, for pedagogical purposes.
  More throughly, it is mean to interface with the nlpeval module, that allows
  interfacing these significance tests in the context of evaluation of NLP
  systems. 

  In case external sources are referenced for further clarification: the 
  link to the external source is added inside the documentation corresponding
  to the documentation.

'''

nCk = lambda n, k: reduce(mul, (Fraction(n-i, i+1) \
    for i in xrange(k)), 1);
binomial_distribution = lambda k, n, p: \
    nCk(n, k)*(p**k)*((1-p)**(n-k));
sign = lambda x, y: \
    1 if y > x else -1 if x > y else 0;
mean = lambda li : sum(li)/len(li);
var  = lambda li, m: sum((x-m)**2 for x in li)/len(li);
sd   = lambda li, m: sqrt(sum((x-m)**2 for x in li)/len(li));

def rankData(valuesList, ties=False):
  from operator import itemgetter;
  frst, scnd = itemgetter(0), itemgetter(1);
  print(valuesList);
  sortedList = sorted(enumerate(valuesList), key=scnd);
  ranks = list(enumerate(sortedList, start=1));
  ranked_values  = ((r, v[1]) for r, v in ranks);
  ranked_indices = ((r, v[0]) for r, v in ranks);

  if ties:
    grouped_ranks = groupby(ranked_values, scnd);
    tied_ranks = [];
    for _, gr in grouped_ranks:
      gr = list(gr);
      tied_ranks.extend(replicate(mean([r for r,v in gr]), len(gr)));
    ranked_indices = [(newrank, oldrank[1]) for oldrank, newrank in zip(ranked_indices, tied_ranks)]
  
  perm_ranks = sorted(ranked_indices, key=scnd);
  return map(frst, perm_ranks);

def sign_test(eval_results1, eval_results2):
  ''' binomial test / sign test '''
  from operator import mul;
  from fractions import Fraction;
  
  pos, neg = 0, 0;
  obser_count = 0;
  for res1, res2 in zip(eval_results1, eval_results2):
    neg += (1 if res1 > res2 else 0);
    pos += (1 if res2 > res1 else 0);
    obser_count += 1;
  return sum(binomial_distribution(x, 0.5, neg+pos) \
      for x in xrange(pos, obser_count+1));

def wilcoxon_rank_test(eval_results1, eval_results2):
  ''' wilcoxon signed rank test '''
  ''' https://en.wikipedia.org/wiki/Wilcoxon_signed-rank_test '''
  absDifference, signs = [], [];
  for res1, res2 in zip(eval_results1, eval_results2):
    if res1 != res2:
      absDifference.append(abs(res1-res2));
      signs.append(sign(res2, res1));
  ranks = rankData(absDifference, ties=True);
  W = sum(s*r for s, r in zip(signs, ranks), 0);
  # -- incomplete
  return 0;

def studentsttest(eval_results1, eval_results2):
  dif = (res2-res1 for res1, res2 in zip(eval_results1, eval_results2));
  m = mean(dif);
  return sqrt(len(dif))*(m/sd(dif, m));

def pratt_rank_test():
  ''' pratt rank test '''
  pass

def zsplit_rank_test():
  ''' zsplit rank test '''
  pass

def ttest():
  ''' Student's t-test '''
  pass

def anova():
  ''' ANOVA '''
  pass

def randomization():
  ''' Randomization test '''
  pass

def bootstrap(eval_results1, eval_results2):
  ''' Bootstrap test '''
  pass

def mcnemarstest(eval_results1, eval_results2):
  pass;

