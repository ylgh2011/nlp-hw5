# Overall desciption

Our algorithm can be summarized batch pairwise rerank optimization with average percptron and extra features. 

# Pairwise rerank optimization with average percptron
In our implementation of pairwise rerank optimization, we use the average percptron instead of the general perceptron algorithm in order to get a steady result of weights. And for to accelarate the procedure of calculating nbests BLEU score, we dump the pre-calculated data file into the directory (data/nbest.ds.gz). Everytime the program is executed, it will first try load this nbest.ds.gz, if not available, it will then do the calculating nbest process.

# Extra features (Ps. All features are already pre-processed in train.nbest and test.nbest)
We added three extra features in our nbests file to improve the final result. 
1. The first feature is based on the sentence length. The value for the feature is functioned with "-abs(len(present translation) - len(correct translation))".
2. The second feature is the count of the untranslated words. It is defined with "-count(word for (word in present translation) && (word not in correct translation) and (word in french sentence))". 
3. The third feature is the the translation score get from ibm model 2. We used the program and the training set in assignment 3 as reference and generated the translation model. We load that model to get the score for each translation.

All of the new values will be non-negative integer and fit the "bigger is better" pattern. For the first two, the correct answer will get the best score (0). For ibm model 2, the correct answer may not be the highest score.

We used a length-adapting reading & operating methods in the program so it can accept any length of input feature lists.


# Final Score:
* The final score (BLEU: 25.96) for our group is produced by running the full text file with the parameters (-t 100000 -x 2000) from the assignment info page on the course website.
** Since we used the translation model trained from the 3rd assignment, we need an additional source file. We will contact you later with an address of that file.
** With all the source files prepared, you can regenerate the result using "python default.py > out.weights"
** The program will change the nbests file so please back-up the original version in advance.

# Warning:
* We make use of some extra features for the nbest file, and as a result, our method will first preprocess the training and testing English file and French file and then rewrite both training and testing nbest files. 
** PS. For IBM model 2 score, we made use of an additional training data of homework 3 and generate dumps of word counts. In the preprocess procedure, we will first read through 2 files and then generate the IBM score for .nbest file. Because these 2 file are too large to be included in the submitted package, we give 2 dropbox links to download these 2 files in the following section


# How to run our program:

1.
Make sure that there are following files under the ./data/ directory
1) test.en
2) test.fr
3) test.nbest (must only has 6 features for each sentence)
4) train.en
5) train.fr
6) train.nbest (must only has 6 initial features for each sentence)
7) ibm2.q.ds.gz (https://www.dropbox.com/s/7xtkm1x82b4gl4w/ibm2.q.ds.gz?dl=0)
8) ibm2.t.ds.gz (https://www.dropbox.com/s/5h03jpj742gk73g/ibm2.t.ds.gz?dl=0)

2.
Make sure you have library.py and final_method.py in the same directory

3.
python final_method.py -t 100000 -x 2000 > f.weights
python rerank.py -w f.weights | python score-reranker.py


# Usage: 
* Command line: python final_method.py [options]

Options:
  -h, --help            show this help message and exit
  -n NBEST, --nbest=NBEST
                        N-best file
  --en=EN               target language references for learning how to rank
                        the n-best list
  -t TAU, --tau=TAU     samples generated from n-best list per input sentence
                        (default 5000)
  -a ALPHA, --alpha=ALPHA
                        sampler acceptance cutoff (default 0.1)
  -x XI, --xi=XI        training data generated from the samples tau (default
                        100)
  -e ETA, --eta=ETA     perceptron learning rate (default 0.1)
  -p EPO, --epo=EPO     number of epochs for perceptron training (default 5)
  --fr=FR               train French file
  --testnbest=TESTNBEST
                        test N-best file
  --testfr=TESTFR       test French file
  --nbestDic=NBESTDS    dumping file of the data structure that storing scores
                        for nbestDic
