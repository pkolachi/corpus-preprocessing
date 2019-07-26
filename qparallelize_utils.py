#!/usr/bin/env python

from __future__ import print_function;

from globalimports import *;
from multiprocessing import Process, Queue, TimeoutError;

def timeout(signum, frame):
  raise MemoryError("Function execution timed out");

def pExecFunction(function, queueIn, queueOut, default_value=None):
  import signal;
  while True:
    idx, value = queueIn.get();
    if idx == None:
      break;
    try:
      #signal.signal(signal.SIGALRM, timeout);
      #signal.alarm(5);
      queueOut.put((idx, function(value)));
      #signal.alarm(0);
    except MemoryError as err: # deprecated without the signal handler
      print(str(err), file=stderr);
      queueOut.put((idx, default_value));
    except TimeoutError as err:
      print(str(err), file=stderr);
      queueOut.put((idx, default_value));
    except Exception as err:
      print(str(err), file=stderr);
      queueOut.put((idx, default_value));

def pExecStarFunction(function, queueIn, queueOut, default_value=None):
  import signal;
  while True:
    idx, value = queueIn.get();
    if idx == None:
      break;
    try:
      #signal.signal(signal.SIGALRM, timeout);
      #signal.alarm(5);
      queueOut.put((idx, function(*value)));
      #signal.alarm(0);
    except MemoryError as err: # deprecated without the signal handler
      print(str(err), file=stderr);
      queueOut.put((idx, default_value));
    except TimeoutError as err:
      print(str(err), file=stderr);
      queueOut.put((idx, default_value));
    except Exception as err:
      print(str(err), file=stderr);
      queueOUt.put((idx, default_value));

def parmap(function, argsList, default_return=None, threads=1, chunksize=500):
  argsList, idxList, jobCount = iter(argsList), counter(0), 0;
  terminateAfterExec, resultsBuffer = False, {};
  inQueue  = Queue(1);
  outQueue = Queue();
  subprocesses = [Process(target=pExecFunction, args=(function, inQueue, outQueue, default_return)) for _ in range(threads)];
  for proc in subprocesses:
    proc.daemon = True;
    proc.start();
  curJobCount = 0;
  while True:
    newArgs = [inQueue.put((idx, args)) for idx, args in zip(islice(idxList, chunksize), islice(argsList, chunksize))];
    jobCount += len(newArgs);
    curJobCount += len(newArgs);
    if len(newArgs) < chunksize:
      [inQueue.put((None, None)) for _ in range(threads)];
      terminateAfterExec = True; 
    print("Feeding %d jobs to the queue, now %d jobs in the queue" %(len(newArgs), curJobCount), file=stderr);
    resultsList = [];
    if terminateAfterExec:
      while len(resultsList) < curJobCount:
        resultsList.append( outQueue.get() );
        [proc.join() for proc in subprocesses];
    else:
      while len(resultsList) < 0.85*curJobCount:
        resultsList.append( outQueue.get() );
    curJobCount -= len(resultsList);
    print("Finished %d jobs in the queue, now %d jobs in the queue" %(len(resultsList), curJobCount), file=stderr);
    resultsBuffer.update(dict((idx, value) for (idx, value) in resultsList));    
    if terminateAfterExec:
      break;
  return [resultsBuffer.get(idx, default_return) for idx in range(jobCount)];

def parstarmap(function, argsList, default_return=None, threads=1, chunksize=500):
  argsList, idxList, jobCount = iter(argsList), counter(0), 0;
  terminateAfterExec, resultsBuffer = False, {};
  inQueue  = Queue(1);
  outQueue = Queue();
  subprocesses = [Process(target=pExecStarFunction, args=(function, inQueue, outQueue, default_return)) for _ in range(threads)];
  for proc in subprocesses:
    proc.daemon = True;
    proc.start();
  curJobCount = 0;
  while True:
    newArgs = [inQueue.put((idx, args)) for idx, args in zip(islice(idxList, chunksize), islice(argsList, chunksize))];
    jobCount += len(newArgs);
    curJobCount += len(newArgs);
    if len(newArgs) < chunksize:
      [inQueue.put((None, None)) for _ in range(threads)];
      terminateAfterExec = True;
    print("Feeding %d jobs to the queue, now %d jobs in the queue" %(len(newArgs), curJobCount), file=stderr);
    resultsList = [];
    if terminateAfterExec:
      while len(resultsList) < curJobCount:
        resultsList.append( outQueue.get() );
        [proc.join() for proc in subprocesses];
    else:
      while len(resultsList) < 0.85*curJobCount:
        resultsList.append( outQueue.get() );
    curJobCount -= len(resultsList);
    print("Finished %d jobs in the queue, now %d jobs in the queue" %(len(resultsList), curJobCount), file=stderr);
    resultsBuffer.update(dict((idx, value) for (idx, value) in resultsList));
    if terminateAfterExec:
      break;
  return [resultsBuffer.get(idx, default_return) for idx in range(jobCount)];

def parimap(function, argsList, default_return=None, threads=1, chunksize=500):
  argsList, idxList, jobCount = iter(argsList), counter(0), 0;
  terminateAfterExec, iterIdx, resultsBuffer = False, 0, {};
  inQueue  = Queue(1);
  outQueue = Queue();
  subprocesses = [Process(target=pExecFunction, args=(function, inQueue, outQueue, default_return)) for _ in range(threads)];
  for proc in subprocesses:
    proc.daemon = True;
    proc.start();
  curJobCount = 0;
  while True:
    newArgs = [inQueue.put((idx, args)) for idx, args in zip(islice(idxList, chunksize), islice(argsList, chunksize))];
    jobCount += len(newArgs);
    curJobCount += len(newArgs);
    if len(newArgs) < chunksize:
      [inQueue.put((None, None)) for _ in range(threads)];
      terminateAfterExec = True; 
    print("Feeding %d jobs to the queue, now %d jobs in the queue" %(len(newArgs), curJobCount), file=stderr);
    resultsList = [];
    if terminateAfterExec:
      while len(resultsList) < curJobCount:
        resultsList.append( outQueue.get() );
        [proc.join() for proc in subprocesses];
    else:
      while len(resultsList) < 0.90*curJobCount:
        resultsList.append( outQueue.get() );
    curJobCount -= len(resultsList);
    print("Finished %d jobs in the queue, now %d jobs in the queue" %(len(resultsList), curJobCount), file=stderr);
    resultsBuffer.update(dict((idx, value) for (idx, value) in resultsList));
    for idx in range(iterIdx, jobCount):
      if not resultsBuffer.has_key(idx):
        iterIdx = idx;
        break;
      yield resultsBuffer[idx];
      del resultsBuffer[idx];
      #print "iteridx=%d\tjobcount=%d" %(iterIdx, jobCount);
    if terminateAfterExec:
      break;
  for idx in range(iterIdx, jobCount):
    if idx in resultsBuffer:
      yield resultsBuffer[idx];
      del resultsBuffer[idx];
    else:
      yield default_return;

def paristarmap(function, argsList, default_return=None, threads=1, chunksize=500):
  argsList, idxList, jobCount = iter(argsList), counter(0), 0;
  terminateAfterExec, iterIdx, resultsBuffer = False, 0, {};
  inQueue  = Queue(1);
  outQueue = Queue();
  subprocesses = [Process(target=pExecStarFunction, args=(function, inQueue, outQueue)) for _ in range(threads)];
  for proc in subprocesses:
    proc.daemon = True;
    proc.start();
  curJobCount = 0;
  while True:
    newArgs = [inQueue.put((idx, args)) for idx, args in zip(islice(idxList, chunksize), islice(argsList, chunksize))];
    jobCount += len(newArgs);
    curJobCount += len(newArgs);
    if len(newArgs) < chunksize:
      [inQueue.put((None, None)) for _ in range(threads)];
      terminateAfterExec = True;
    print("Feeding %d jobs to the queue, now %d jobs in the queue" %(len(newArgs), curJobCount), file=stderr);
    resultsList = [];
    if terminateAfterExec:
      while len(resultsList) < curJobCount:
        resultsList.append( outQueue.get() );
        [proc.join() for proc in subprocesses];
    else:
      while len(resultsList) < 0.85*curJobCount:
        resultsList.append( outQueue.get() );
    curJobCount -= len(resultsList);
    print("Finished %d jobs in the queue, now %d jobs in the queue" %(len(resultsList), curJobCount), file=stderr);
    resultsBuffer.update(dict((idx, value) for (idx, value) in resultsList));
    for idx in range(iterIdx, jobCount):
      if not resultsBuffer.has_key(idx):
        iterIdx = idx;
        break;
      yield resultsBuffer[idx];
      del resultsBuffer[idx];
    if terminateAfterExec:
      break;
  for idx in range(iterIdx, jobCount):
    if idx in resultsBuffer:
      yield resultsBuffer[idx];
      del resultsBuffer[idx];
    else:
      yield default_return;

