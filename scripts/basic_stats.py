
import numpy as np;
import scipy.stats as stats;

def rank_spearmansp(iter1, iter2):
  X = np.fromiter(iter1, dtype='float64');
  Y = np.fromiter(iter2, dtype='float64');
  return stats.spearmanr(X, Y);

def kendalls_tau(iter1, iter2):
  X = np.fromiter(iter1, dtype='float64');
  #rank_X = stats.rankdata(X, method='min'); # CURRENT VERSION DOES NOT SUPPORT TIE-DISTINCTIONS
  rank_X = stats.rankdata(X);
  Y = np.fromiter(iter2, dtype='float64');
  #rank_Y = stats.rankdata(Y, method='min');
  rank_Y = stats.rankdata(Y);
  return stats.spearmanr(rank_X, rank_Y);

def kruskals_gamma():
  pass;
