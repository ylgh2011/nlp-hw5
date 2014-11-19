# Overall desciption

Our algorithm can be summarized batch pairwise rerank optimization with average percptron and extra features. 

# Pairwise rerank optimization with average percptron
In our implementation of pairwise rerank optimization, we use the average percptron instead of the general perceptron algorithm in order to get a steady result of weights. And for to accelarate the procedure of calculating nbests BLEU score, we dump the pre-calculated data file into the directory (data/nbest.ds.gz). Everytime the program is executed, it will first try load this nbest.ds.gz, if not available, it will then do the calculating nbest process.

# Extra features (Ps. All features are already pre-processed in train.nbest and test.nbest)
We added three extra features in our nbests file to improve the final result. 
1. The first feature is based on the sentence length. The value for the feature is functioned with "-abs(len(present translation) - len(correct translation))".
2. The second feature is the count of the untranslated words. It is defined with "-count(word for (word in present translation) && (word not in correct translation) and (word in french sentence))". 
3. The third feature is the the translation score get from ibm model 1. We used the program and the training set in assignment 3 as reference and generated the translation model. We load that model to get the score for each translation.

All of the new values will be non-negative integer and fit the "bigger is better" pattern. For the first two, the correct answer will get the best score (0). For ibm model 1, the correct answer may not be the highest score.

We used a length-adapting reading & operating methods in the program so it can accept any length of input feature lists.


# Final Score:
* The final score (BLEU: 25.596) for our group is produced by running the full text file with the default parameters from the assignment info page on the course website.
** Since we used the translation model trained from the 3rd assignment, we need an additional source file. We will contact you later with an address of that file.
** With all the source files prepared, you can regenerate the result using "python default.py > out.weights"
** The program will change the nbests file so please back-up the original version in advance.

# Warning:
* We make use of some extra features for the nbest file, and as a result, our method will first preprocess the training and testing English file and French file and then rewrite both training and testing nbest files. 
** PS. For IBM model 1 score, we made use of an additional training data of homework 3 and generate a dump of word count. In the preprocess procedure, we will first read through this file and then generate the IBM score for nbest file. 

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
