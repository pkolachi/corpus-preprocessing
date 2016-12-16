
import multiprocessing;

FUNC_OBJ = None;

''' This was included in case arguments to
the function are shared using generators;
in which case Python does not allow you
to do this since generators are not thread-safe'''
class LockedIterator(object):
  def __init__(self, it):
    self._lock = multiprocessing.Lock(); 
    self._it = iter(it);
  def __iter__(self):
    return self;
  def next(self):
    self._lock.acquire();
    try:
      res = next(self._it);
    except StopIteration:
      self._lock.release();
      raise StopIteration;
    self._lock.release();
    return res;
  __next__ = next;

def pExecFunction(arguments):
  return FUNC_OBJ(arguments) if FUNC_OBJ else None;

def pExecStarFunction(arguments):
  return FUNC_OBJ(*arguments) if FUNC_OBJ else None;

class PMapReduce:
  pool = None;
  def parmap(self, function, argsList, workers=1, chunksize=500):
    global FUNC_OBJ;
    FUNC_OBJ = function;
    if pool is None:
      pool = multiprocessing.Pool(workers);
    results = pool.map(pExecFunction, argsList, chunksize=chunksize);
    pool.close();
    pool.join();
    return results;

  def parstarmap(self, function, argsList, workers=1, chunksize=500):
    global FUNC_OBJ;
    FUNC_OBJ = function;
    if pool is None:
      pool = multiprocessing.Pool(workers);
    results = pool.map(pExecStarFunction, argsList, chunksize=chunksize);
    pool.close();
    pool.join();
    return results;

  def parimap(function, argsList, workers=1, chunksize=500):
    global FUNC_OBJ;
    FUNC_OBJ = function;
    if pool is None:
      pool = multiprocessing.Pool(workers);
    for res in pool.imap(pExecFunction, argsList, chunksize=chunksize):
      yield res;
    pool.close();
    pool.join();

def paristarmap(function, argsList, workers=1, chunksize=500):
  global FUNC_OBJ;
  FUNC_OBJ = function;
  pool = multiprocessing.Pool(workers);
  for res in pool.imap(pExecStarFunction, argsList, chunksize=chunksize):
    yield res;
  pool.close();
  pool.join();

