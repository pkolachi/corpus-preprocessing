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
    self.scores = defaultdict(lambda: []);
    self._names = [('poseval-p', 'POS Precision'), \
        ('poseval-unk-p', 'POS Precision (u)'), \
        ('las-p', 'LAS Precision'), \
        ('uas-p', 'UAS Precision'), \
        ('las-unk-p', 'LAS Precision (u)'), \
        ('uas-unk-p', 'UAS Precision (u)'), \
        ('lemma-p', 'Lemma Precision'), \
        ('lemma-unk-p', 'Lemma Precision (u)')];
    self.names = dict(self._names);

  def summarize(self):
    summary = [];
    # address how many words have been replaced by the mechanism;
    correct = sum(replaced for replaced, total in self.scores['eval-unk-repl']);
    total   = sum(total    for replaced, total in self.scores['eval-unk-repl']);
    summary.append("Unknown replaced:%d %d" %(correct, total));
    for prop, propname in self._names:
      if prop not in self.scores:
        continue;
      # calculate aggregates;
      #correct = sum(correct for correct, total in self.scores[prop]);
      #total   = sum(total   for correct, total in self.scores[prop]);
      #total   = 1 if not total else total;
      summary.append("%s:%.4f" %(propname, self.average(prop)));
    return '\t'.join(summary);

  def average(self, prop):
    correct = sum(correct for correct, total in self.scores[prop]);
    total   = sum(total   for correct, total in self.scores[prop]);
    total   = 1 if not total else total;
    return correct/total;

  def microaverage(self, prop):
    total   = sum(total   for correct, total in self.scores[prop]);
    total   = 1 if not total else total;
    average = 0;
    for correct, full in self.scores[prop]:
      average += correct/total; #(correct/full)*(full/total);
    return average;

  def set_properties(self, props):
    for p in props:
      self.scores[p] = [(0,1)];

def evaluate(gconll_list, pconll_list, metric='depeval', options={'precision': True}):
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
    train_vcb = dict((word, True) for word in random_utils.lines_from_file(def_options['train-vcb']));
  else:
    train_vcb = dict();

  gconll_list, pconll_list = list(gconll_list), list(pconll_list);

  if metric in ['poseval', 'depeval'] and def_options['precision']:
    predfieldname = 'ppostag' if def_options['format'] == 'conll09' else 'cpostag';
    goldfieldname = 'postag'  if def_options['format'] == 'conll09' else 'cpostag';
    for gsent, psent in izip(gconll_list, pconll_list):
      correct = sum(1 if gedge[goldfieldname] == pedge[predfieldname] else 0 for gedge, pedge in zip(gsent, psent));
      total = len(gsent);
      res.scores['poseval-p'].append((correct, total));
      if def_options['unknown']:
        correct = sum(1 if gedge[goldfieldname] == pedge[predfieldname] else 0 for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        total   = sum(1 if gedge['form'] not in train_vcb else 0 for gedge in gsent);
        res.scores['poseval-unk-p'].append((correct, total));
        replaced = sum(1 if pedge['lemma'] not in ['<unknown>', '_'] else 0 for pedge in psent);
        res.scores['eval-unk-repl'].append((replaced, total));
  if metric == 'depeval' and def_options['precision']:
    predhead = 'phead' if def_options['format'] == 'conll09' else 'head';
    goldhead = 'head';
    predrel  = 'pdeprel' if def_options['format'] == 'conll09' else 'deprel';
    goldrel  = 'deprel';
    for gsent, psent in izip(gconll_list, pconll_list):
      correct = sum(1 if gedge[goldhead] == pedge[predhead] else 0 for gedge, pedge in zip(gsent, psent));
      total = len(gsent);
      res.scores['uas-p'].append((correct, total));
      correct = sum(1 if (gedge[goldrel] == pedge[predrel] and gedge[goldhead] == pedge[predhead]) else 0 for gedge, pedge in zip(gsent, psent));
      res.scores['las-p'].append((correct, total));
      if def_options['unknown']:
        correct = sum(1 if gedge[goldhead] == pedge[predhead] else 0 for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        total   = sum(1 if gedge['form'] not in train_vcb else 0 for gedge in gsent);
        res.scores['uas-unk-p'].append((correct, total));
        correct = sum(1 if gedge[goldrel] == pedge[predrel] else 0 for gedge, pedge in zip(gsent, psent) if gedge['form'] not in train_vcb);
        res.scores['las-unk-p'].append((correct, total));

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
  import os, time, random;
  log_text = [];
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
    log_text.append('Is model-2 better than model-1 for %s: %s' %(eval_results1.names[propname], 'True' if differences[propname] > 0 else 'False'));
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
  for propname in props:
    log_text.append('Is model-2 better than model-1 (p-value) for %s: %.4f' %(eval_results1.names[propname], (random_trials[propname]+1)/(trials+1)));
  return '\n'.join(log_text);

if __name__ == '__main__':
  import os;
  if sysargv[1].endswith('conll09'):
    evaloptions = {'format': 'conll09'};   
    conll_utils.FIELDS = conll_utils.CONLL09_COLUMNS;
  else:
    evaloptions = {'format': 'conll'};     
    conll_utils.FIELDS = conll_utils.CONLL07_COLUMNS;
  if len(sysargv) > 3:
    evaloptions['unknown'] = True;
    evaloptions['train-vcb'] = sysargv[len(sysargv)-1];
  full_results = [];
  for systemfile in sysargv[2:-1]:
    with random_utils.smart_open(sysargv[1]) as infile1, random_utils.smart_open(systemfile) as infile2:
      #print("Gold file:%s\tSystem file:%s" %(sysargv[1], sysargv[2]));
      gold_conllsent = conll_utils.sentences_from_conll(infile1);
      sys_conllsent  = conll_utils.sentences_from_conll(infile2);
      full_results.append( (systemfile, evaluate(gold_conllsent, sys_conllsent, metric='depeval', options=evaloptions)) );
  for systemfile, results in full_results:
    #print("%s\t%s" %(os.path.split(systemfile)[1], full_results[-1].summarize()));
    print("%s\t%s" %(systemfile, results.summarize()));

  #'''
  import itertools;
  pairs = itertools.product([0], range(1, len(full_results)));
  #pairs = itertools.combinations(xrange(len(full_results)), 2);
  for m1idx, m2idx in pairs:
    print('Testing significance for %s and %s' %(full_results[m1idx][0], full_results[m2idx][0]));
    print(randomized_comparator(full_results[m1idx][1], full_results[m2idx][1], props=['poseval-p', 'poseval-unk-p', 'las-p', 'las-unk-p', 'uas-p', 'uas-unk-p']));
    print('='*100+'\n');
  #'''
