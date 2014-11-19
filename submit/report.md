# Overall desciption

Our algorithm can be summarized as an IBM model 2 with bidirection agree voiting, intersection and diagonal heuristic operation

# Pairwise rerank optimization with average percptron

After failing to implement a real HMM based model, we adapt a cheaper noisy-channel model, which is IBM model 2. According to its definition, an IBM-M2 model consists of a finite set E of English words, a set F of French words, and integers M and L specifying the maximum length of French and English sentences respectively. The parameters of the model are as follows:
    Translation parameter t(f | e) - conditional probability of generating French word f from English word e.
    Distortion paramter q(j | i, l, m) - probability of alignment variable ai taking the value j, conditioned on the lengths l and m of the English and French sentences.
We will make an independence assumption of this model and use an interative method with parameter estimation for the training phase. There is some modification to this certain implementation of IBM model 2 so as to improve its performance with German alignment. And those techniques are addressed in the following sections 

# Extra features

While using IBM model 2 to update the dictionary Pr(f | e) (probability of a Franch word given an English word), we maintain another dictionary Pr(e | f) (probability of an English word given a Franch word) at the same time.And according to the result of paper 'Alignment by Agreement', we modify the classic IBM model 2 by using joint probablity for calculating the estimated alignment count. And furthur more we apply the add-n smoothing to the probability calculating, in order to smooth the align confidence of the model.

After the training phase (several iterations), the alignment between a pair of words (f_i, e_j) is decided by the product of Pr( f_i | e_j ) and Pr( e_j | f_i ) instead of a single probability.


# Final Score:
* The final score (AER: 0.266) for our group is produced by running the full text file for 10 times with penalty value of 0.85
** You could replicate the result by following command
*** python final_method.py -p europarl -f de -i 10 -t 0.85 > out.a 
** Please notice that with this method, it will consume about 2 hours to complete the align procedure, the memory space this method will take is around 12 GB

# Usage: 
* Command line: python final_method.py [options]
Options:
  -h, --help            show this help message and exit
  -d DATADIR, --datadir=DATADIR
                        data directory (default=data)
  -p FILEPREFIX, --prefix=FILEPREFIX
                        prefix of parallel data files (default=hansards)
  -e ENGLISH, --english=ENGLISH
                        suffix of English (target language) filename
                        (default=en)
  -f FRENCH, --french=FRENCH
                        suffix of French (source language) filename
                        (default=fr)
  -l LOGFILE, --logfile=LOGFILE
                        filename for logging output
  -n NUM_SENTS, --num_sentences=NUM_SENTS
                        Number of sentences to use for training and alignment
  -i ITERATION, --iteration=ITERATION
                        The iteration number for the alignment learning.
  -t PENALTY, --penalty=PENALTY
                        pow(pe, abs(i-j))