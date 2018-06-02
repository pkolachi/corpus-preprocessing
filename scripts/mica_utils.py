# Interface to the MICA parser

def normalizeToken(token):
  token = token.replace('#', '_HASH_');
  token = token.replace(':', '_COLON_');
  token = token.replace('%', '_PERCENTAGE_');
  token = token.replace(',', '_COMMA_');
  token = token.replace('.', '_PERIOD_');
  token = token.replace('?', '_QMARK_');
  return token;

def parseMicaOutput(outputFile):
  pass;

def runSupertagger(sentencesList):
  for sentence in sentencesList:
    yield '';

def runParser(sentencesList):
  for sentence in sentencesList:
    yield '';

def distinguishArgumentAdjunctTokens(sentencesList):
  for sentence in sentencesList:
    yield '';

if __name__ == '__main__':
  main();
