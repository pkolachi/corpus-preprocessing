

bigrams :: Tokens -> FreqTable
bigrams words = pairs 
   where
      padseq = ["<s>"] + words + ["</s>"]
      pairs  = [(w, w_, 1) | w, w_ <- zip(words, tail words)]

