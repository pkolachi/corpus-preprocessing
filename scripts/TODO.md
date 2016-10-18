PORTING from Python 2 to Python 3

== checked scripts:
    cmpDirectories.py
    stanforddependencyconverter.py
    alt_unigoogle_utils.py

== exceptions:
    alt_unigoogle_utils.py (does not work in Python3, writing to file has to be fixed and lambda functions are not picklable- so threads mode fails)


- added globalimports.py 
  - this should be kept uniform to let all scripts use these basic imports;
  - ONLY basic imports are put in this file, mainly to ensure that codes are 
  compatible with both 2 and 3 and to avoid any resistance to use more 
  flexible but obscure facilities in Python (for example, defaultdict is a
  good example).
  - the imports try to maximally expose the Python 3 interface; so map 
  behaves like imap in Python 2 but takes default behavior in Python 3. 


=======================

- Generic scripts: 
  - re-use functions in random_utils to ensure uniformity across processing
  scripts;
  - re-use functions in parallelize_utils to ensure uniformity across 
  multiprocessing scripts;
    - check if putting and taking things in queues is an acceptable overhead
      (compared to using pools)
    - apparently, using generators across threads raises 
      `Valueerror: generator already in execution`. So, the current 
      parallelize_utils does not work. Fix this. 

stanford_corenlp_utils.py


add syntactic category information to prune entries in phrase-table; compute normalized prob scores from weights in tuned model; 
term indexing; - building trie structure for n-best trees
Add argparse utility to allow for command-line arguments. Current available facilities are 