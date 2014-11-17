#!/usr/bin/env python
import optparse, sys, os
from collections import namedtuple, defaultdict
from bleu import bleu_stats, bleu, smoothed_bleu
from operator import itemgetter
import itertools
import random
from math import fabs
optparser = optparse.OptionParser()
optparser.add_option("-n", "--nbest", dest="nbest", default=os.path.join("data", "train.nbest"), help="N-best file")
optparser.add_option("--en", dest="en", default=os.path.join("data", "train.en"), help="target language references for learning how to rank the n-best list")
optparser.add_option("-t", "--tau", dest="tau", default=5000, help="samples generated from n-best list per input sentence (default 5000)")
optparser.add_option("-a", "--alpha", dest="alpha", default=0.1, help="sampler acceptance cutoff (default 0.1)")
optparser.add_option("-x", "--xi", dest="xi", default=100, help="training data generated from the samples tau (default 100)")
optparser.add_option("-e", "--eta", dest="eta", default=0.1, help="perceptron learning rate (default 0.1)")
optparser.add_option("-p", "--epo", dest="epo", default=5, help="number of epochs for perceptron training (default 5)")

(opts, _) = optparser.parse_args()
def main():
    nbests = defaultdict(list)
    references = {}
    for i, line in enumerate(open(opts.en)):
        '''
        Initialize references to correct english sentences
        '''
        references[i] = line

    for line in open(opts.nbest):
        (i, sentence, features) = line.strip().split("|||")
        stats =  list(bleu_stats(sentence, references[int(i)]))
        bleu_score = bleu(stats)
        smoothed_bleu_score = smoothed_bleu(stats)
        # making the feature string to float list 
        feature_list = [float(x) for x in features.split()]
        nbests[int(i)].append((sentence, bleu_score, smoothed_bleu_score, feature_list))

    theta = [1.0/6 for _ in xrange(6)] #initialization
    

    for i in range(0, opts.epo):
        mistake = 0;
        for nbest in nbests:
            sample = get_sample(nbests[nbest])
            sample.sort(key=lambda i: i[0][2] - i[1][2], reverse=True)
            for i in range(0, min(len(sample), opts.xi)):
                for j in range(0, 6):
                    if theta[j] * sample[i][0][3][j] <= theta[j] * sample[i][1][3][j]:
                        mistake = mistake + 1
                        theta[j] = theta[j] + opts.eta * (sample[i][0][3][j] - sample[i][1][3][j])
        sys.stderr.write("Mistake:  %s\n" % (mistake,))
    print "\n".join([str(weight) for weight in theta])

def get_sample(nbest):
    '''
    nbest is a list of [setence, bleu_score, smoothed_bleu_score, featrue_list]
    We only use bleu_socre and smoothed_bleu_score here
    '''

    # sort the nbest list of decreasing order on bleu_score
    nbest.sort(key=itemgetter(1), reverse=True) 
 
    # generate all the pairs combinations
    # len(pairs) = len(nbest) * (len(nbest) - 1) / 2
    pairs = list(itertools.combinations(range(0, len(nbest)), 2))
    random.shuffle(pairs)


    samples = [];
    for pair in pairs:
        # pair will be random pair index from nbest
        if len(samples) >= opts.tau:
            break
        if fabs(nbest[pair[0]][2] - nbest[pair[1]][2]) > opts.alpha:
            samples.append((nbest[pair[0]], nbest[pair[1]]))
        else:
            continue
    return samples

if __name__ == '__main__':
    main()
