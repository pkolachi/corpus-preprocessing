#!/usr/bin/env python

from __future__ import print_function, division;

from globalimports import *;
import conll_utils;
import random_utils; 

class EvaluationResult:
  def __init__(self):
    # a dictionary object;
    # each key represents a property that is being evaluated
    # for e.g, key can be 'precision', 'recall', 'precision of unknown' so on 
    self.scores = defaultdict(list);
    self._names = [('poseval-p', 'POS Precision'), \
        ('poseval-unk-p', 'POS Precision (u)'), \
        ('las-p', 'LAS Precision'), \
        ('uas-p', 'UAS Precision'), \
        ('lacc-p', 'LAcc Precision'), \
        ('las-unk-p', 'LAS Precision (u)'), \
        ('uas-unk-p', 'UAS Precision (u)'), \
        ('lacc-unk-p', 'LAcc Precision (u)'), \
        ('lemma-p', 'Lemma Precision'), \
        ('lemma-unk-p', 'Lemma Precision (u)')];
    self.names = dict(self._names);

  def summarize(self):
    summary = [];
    # address how many words have been replaced by the mechanism;
    correct = sum(replaced for replaced, total, _ \
        in self.scores['eval-unk-repl']);
    total   = sum(total    for replaced, total, _ \
        in self.scores['eval-unk-repl']);
    summary.append("Unknown replaced:%d %d(%.3f)" \
        %(correct, total, 100*(correct/total)));
    for prop, propname in self._names:
      if prop not in self.scores:
        continue;
      summary.append("%s:%.4f" %(propname, self.average(prop)));
    return '\t'.join(summary);

  def average(self, prop):
    correct = sum(correct for correct, total, _ in self.scores[prop]);
    total   = sum(total   for correct, total, _ in self.scores[prop]);
    total   = 1 if not total else total;
    return correct/total;

  def microaverage(self, prop):
    total   = sum(total   for correct, total, _ in self.scores[prop]);
    total   = 1 if not total else total;
    average = sum(correct/total for correct, full, _ in self.scores[prop]);
    #for correct, full in self.scores[prop]: average += correct/total; #(correct/full)*(full/total);
    return average;

  def set_properties(self, props):
    for p in props:
      self.scores[p] = [(0,1)];

def evaluate(gconll_list, pconll_list, metric='depeval', \
    options={'precision': True}):
  res = EvaluationResult();
  if metric not in ['poseval', 'depeval', 'lemmaeval']:
    print('Unknown evaluation metric as input: %s', file=stderr);
    return res;

  def_options = {'precision': True, \
      'recall': False,
      'sigtest': False,
      'unknown': False,
      'train-vcb': '',
      'format': 'conll07'
      };
  def_options.update(options);
  
  if def_options['unknown']:
    train_vcb = dict((word, True) for word in \
        random_utils.lines_from_file(def_options['train-vcb']));
  else:
    train_vcb = dict();

  gconll_list, pconll_list = list(gconll_list), list(pconll_list);

  if metric in ['poseval', 'depeval'] and def_options['precision']:
    predfieldname = 'ppostag' if def_options['format'] == 'conll09' else 'cpostag';
    goldfieldname = 'postag'  if def_options['format'] == 'conll09' else 'cpostag';
    for gsent, psent in izip(gconll_list, pconll_list):
      correct      = sum(1 if gedge[goldfieldname] == pedge[predfieldname] else 0 for gedge, pedge in zip(gsent, psent));
      correct_repr = ''.join('1' if gedge[goldfieldname] == pedge[predfieldname] else '0' for gedge, pedge in zip(gsent, psent));
      total = len(gsent);
      res.scores['poseval-p'].append((correct, total, correct_repr));
      if def_options['unknown']:
        correct = sum(1 if gedge[goldfieldname] == pedge[predfieldname] else 0 for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        correct_repr = ''.join('1' if gedge[goldfieldname] == pedge[predfieldname] else '0' for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        total   = sum(1 if gedge['form'] not in train_vcb else 0 for gedge in gsent);
        res.scores['poseval-unk-p'].append((correct, total, correct_repr));
        replaced = sum(1 if pedge['lemma'] not in ['<unknown>', '_'] else 0 for pedge in psent);
        replaced_repr = ''.join('1' if pedge['lemma'] not in ['<unknown>', '_'] else '0' for pedge in psent);
        res.scores['eval-unk-repl'].append((replaced, total, replaced_repr));
  if metric == 'depeval' and def_options['precision']:
    predhead = 'phead' if def_options['format'] == 'conll09' else 'head';
    goldhead = 'head';
    predrel  = 'pdeprel' if def_options['format'] == 'conll09' else 'deprel';
    goldrel  = 'deprel';
    for gsent, psent in izip(gconll_list, pconll_list):
      correct = sum(1 if gedge[goldhead] == pedge[predhead] else 0 for gedge, pedge in zip(gsent, psent));
      correct_repr = ''.join('1' if gedge[goldhead] == pedge[predhead] else '0' for gedge, pedge in zip(gsent, psent));
      total = len(gsent);
      res.scores['uas-p'].append((correct, total, correct_repr));
      correct = sum(1 if (gedge[goldrel] == pedge[predrel] and gedge[goldhead] == pedge[predhead]) else 0 for gedge, pedge in zip(gsent, psent));
      correct_repr = ''.join('1' if (gedge[goldrel] == pedge[predrel] and gedge[goldhead] == pedge[predhead]) else '0' for gedge, pedge in zip(gsent, psent));
      res.scores['las-p'].append((correct, total, correct_repr));
      correct = sum(1 if gedge[goldrel] == pedge[predrel] else 0 for gedge, pedge in zip(gsent, psent));
      correct_repr = ''.join('1' if gedge[goldrel] == pedge[predrel] else '0' for gedge, pedge in zip(gsent, psent));
      res.scores['lacc-p'].append((correct, total, correct_repr));
      if def_options['unknown']:
        correct = sum(1 if gedge[goldhead] == pedge[predhead] else 0 for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        correct_repr = ''.join('1' if gedge[goldhead] == pedge[predhead] else '0' for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        total   = sum(1 if gedge['form'] not in train_vcb else 0 for gedge in gsent);
        res.scores['uas-unk-p'].append((correct, total, correct_repr));
        correct = sum(1 if (gedge[goldrel] == pedge[predrel] and gedge[goldhead] == pedge[predhead]) else 0 for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        correct_repr = ''.join('1' if (gedge[goldrel] == pedge[predrel] and gedge[goldhead] == pedge[predhead]) else '0' for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        res.scores['las-unk-p'].append((correct, total, correct_repr));
        correct = sum(1 if gedge[goldrel] == pedge[predrel] else 0 for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        correct_repr = ''.join('1' if gedge[goldrel] == pedge[predrel] else '0' for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        res.scores['lacc-unk-p'].append((correct, total, correct_repr));

  return res;

def mtevaluate(gold_hyps, sys_hyps, metric='bleu', options={'brevity': 'closest'}):

  if metric not in ['bleu', 'ter', 'meteor']:
    print("unknown metric", metric);
  return;

'''
Matched-pair t
Sign and Wilcoxon tests
  - to handle the mis-assumption that techniques being compared produce independent results
  - works for recall
  - not for precision or F-score

Randomization test (Cohen 1995)
  - for precision and F-score
'''
def randomized_comparator(eval_results1, eval_results2, props=['las-p', 'las-unk-p', 'uas-p', 'uas-unk-p'], trials=10000):
  '''
     modified this function to only return p-values list for each metric in props
  '''

  import os, time, random;
  #log_text = [];   ## modifie
  pvalues = [];
  pid = os.getpid();
  if not trials:
    trials = 1;
  differences = {};
  for propname in props:
    model1_score = eval_results1.microaverage(propname);
    model2_score = eval_results2.microaverage(propname);
    differences[propname] = model2_score-model1_score;
    #log_text.append('%s for model-1: %.4f' %(eval_results1.names[propname], model1_score));
    #log_text.append('%s for model-2: %.4f' %(eval_results2.names[propname], model2_score));
    #log_text.append('Is model-2 better than model-1 for %s: %s' %(eval_results1.names[propname], 'True' if differences[propname] > 0 else 'False'));
  samples_count = len(eval_results1.scores[propname]);
  random_trials = dict((propname, 0) for propname in props);
  local_results1, local_results2 = eval_results1, eval_results2;
  random.seed(int(time.time()) ^ (pid+(pid<<15)));
  for i in xrange(1, trials+1):
    if not i%1000:
      print('(%d)...' %(i), end=' ', file=stderr);
    shufeval_results1, shufeval_results2 = EvaluationResult(), EvaluationResult();
    count = 0;
    for idx in xrange(samples_count):
      if random.random() > 0.5:
        for propname in props:
          shufeval_results2.scores[propname].append(local_results1.scores[propname][idx]);
          shufeval_results1.scores[propname].append(local_results2.scores[propname][idx]);
      else:
        for propname in props:
          shufeval_results1.scores[propname].append(local_results1.scores[propname][idx]);
          shufeval_results2.scores[propname].append(local_results2.scores[propname][idx]);
    for propname in props:
      model1_score = shufeval_results1.microaverage(propname);
      model2_score = shufeval_results2.microaverage(propname);
      shuf_difference = model2_score-model1_score;
      if   differences[propname] >= 0 and shuf_difference >= differences[propname]:
        random_trials[propname] += 1;
      elif differences[propname] < 0  and shuf_difference <= differences[propname]:
        random_trials[propname] += 1;
    local_results1 = shufeval_results1;
    local_results2 = shufeval_results2;
  print('', file=stderr);
  #for propname in props:
  #  log_text.append('Is model-2 better than model-1 (p-value) for %s: %.4f' %(eval_results1.names[propname], (random_trials[propname]+1)/(trials+1)));
  pvalues = [(random_trials[propname]+1)/(trials+1) for propname in props];
  return pvalues;

def mcnemar(eval_results1, eval_results2, props=['las-p', 'las-unk-p', 'uas-p', 'uas-unk-p']):
  samples_count = len(eval_results1.scores[props[0]]);
  from math import erf, sqrt;
  zvalue2pvalue = lambda zvalue: 0.5*(1+erf(-zvalue/sqrt(2)));  # alternatively, scipy.stats has norm.sf
  pvalues = [];
  for propname in props:
    bothtrue, bothfalse, truefalse, falsetrue = 0, 0, 0, 0;
    for idx in xrange(samples_count):
      if len(eval_results1.scores[propname][idx][2]) != len(eval_results2.scores[propname][idx][2]): 
        continue;
      bothtrue  += sum(1 if ch1 == '1' and ch1 == ch2 else 0 for ch1, ch2 in izip(eval_results1.scores[propname][idx][2], eval_results2.scores[propname][idx][2]));
      bothfalse += sum(1 if ch1 == '0' and ch1 == ch2 else 0 for ch1, ch2 in izip(eval_results1.scores[propname][idx][2], eval_results2.scores[propname][idx][2]));
      truefalse += sum(1 if ch1 == '1' and ch1 != ch2 else 0 for ch1, ch2 in izip(eval_results1.scores[propname][idx][2], eval_results2.scores[propname][idx][2]));
      falsetrue += sum(1 if ch1 == '0' and ch1 != ch2 else 0 for ch1, ch2 in izip(eval_results1.scores[propname][idx][2], eval_results2.scores[propname][idx][2]));
    zvalue = abs(truefalse-falsetrue)/sqrt(truefalse+falsetrue) if (truefalse+falsetrue) else 0;
    # Using two-tailed tests to convert zvalue to pvalue; 
    pvalue = zvalue2pvalue(zvalue)*2; 
    pvalues.append(pvalue);
  return pvalues;


if __name__ == '__main__':
  import os;
  if sysargv[1].endswith('conll09'):
    evaloptions = {'format': 'conll09'};   
    conll_utils.FIELDS = conll_utils.CONLL09_COLUMNS;
  else:
    evaloptions = {'format': 'conll'};     
    conll_utils.FIELDS = conll_utils.CONLL07_COLUMNS;
  
  if len(sysargv) > 3 and sysargv[-1].endswith('.vcb'):
    evaloptions['unknown'] = True;
    evaloptions['train-vcb'] = sysargv[len(sysargv)-1];
  else:
    evaloptions['unknown'] = False;
  
  full_results = [];
  full_results_summary = [];
  
  oov_props = ['poseval-p', 'poseval-unk-p', 'las-p', 'uas-p', 'lacc-p', 'las-unk-p', 'uas-unk-p', 'lacc-unk-p'];

  for systemfile in (sysargv[2:-1] if evaloptions['unknown'] else sysargv[2:]):
    with random_utils.smart_open(sysargv[1]) as infile1, random_utils.smart_open(systemfile) as infile2:
      #print("Gold file:%s\tSystem file:%s" %(sysargv[1], sysargv[2]));
      gold_conllsent = conll_utils.sentences_from_conll(infile1);
      sys_conllsent  = conll_utils.sentences_from_conll(infile2);
      full_results.append( (systemfile, evaluate(gold_conllsent, sys_conllsent, metric='depeval', options=evaloptions)) );
      full_results_summary.append( (systemfile, full_results[-1][1].summarize()) );
  #for systemfile, results in full_results: print("%s\t%s" %(systemfile, results.summarize()));

  import itertools;
  pairs = itertools.product([0], range(1, len(full_results)));
  #pairs = itertools.combinations(xrange(len(full_results)), 2);
  pairwise_pvalues = [];
  for m1idx, m2idx in pairs:
    #print('Testing significance for %s and %s' %(full_results[m1idx][0], full_results[m2idx][0]), file=stderr);
    #pvalues = randomized_comparator(full_results[m1idx][1], full_results[m2idx][1], props=oov_props);
    pvalues = mcnemar(full_results[m1idx][1], full_results[m2idx][1], props=oov_props);
    pairwise_pvalues.append(pvalues);

  pairs = itertools.product([0], range(1, len(full_results)));
  TABLE = [];
  TABLE.append([full_results_summary[0][0]] + full_results_summary[0][1].split('\t'));
  for pairidx, pvalues in izip(pairs, pairwise_pvalues):
    md1idx, m2idx = pairidx;
    text_scores = full_results_summary[m2idx][1].split('\t');
    sigtext_scores = [text_scores[0]] + ['%s(%.2f)' %(score, pval) for score, pval in izip(text_scores[1:], pvalues)]; 
    TABLE.append([full_results_summary[m2idx][0]] + sigtext_scores);

  max_col_widths = [max(len(entry) for entry in map(itemgetter(idx), TABLE)) for idx in xrange(10)];
  for row in TABLE:
    print('\t'.join(entry.ljust(width) for entry, width in izip(row, max_col_widths)));

  exit(0);
