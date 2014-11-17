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
entry = namedtuple("entry", "sentence, bleu_score, smoothed_bleu, feature_list")


def get_sample(nbest):
    '''
    nbest is a list of [setence, bleu_score, smoothed_bleu_score, featrue_list]
    We only use bleu_socre and smoothed_bleu_score here
    '''

    # generate all the pairs combinations
    # len(pairs) = len(nbest) * (len(nbest) - 1) / 2
    pairs = list(itertools.combinations(range(0, len(nbest)), 2))
    random.shuffle(pairs)


    samples = [];
    for pair in pairs:
        # pair will be random pair index from nbest
        if len(samples) >= opts.tau:
            break
        if fabs(nbest[pair[0]].smoothed_bleu - nbest[pair[1]].smoothed_bleu) > opts.alpha:
            if nbest[pair[0]].smoothed_bleu > nbest[pair[1]].smoothed_bleu:
                samples.append((nbest[pair[0]], nbest[pair[1]]))
            else:
                samples.append((nbest[pair[1]], nbest[pair[0]]))
        else:
            continue
    return samples


def dot_product(l1, l2):
    if (len(l1) != len(l2)):
        raise(ValueError, "product of dif length of vectors")
    ans = 0.0
    for i in xrange(len(l1)):
        ans += l1[i] * l2[i]
    return ans


def vector_plus(v1, v2, multiply=1):
    ans = []
    for i in xrange(len(v1)):
        ans.append(v1[i] + multiply * v2[i])
    return ans


def main():
    nbests = []
    references = []
    sys.stderr.write("Reading English Sentences")
    for i, line in enumerate(open(opts.en)):
        '''Initialize references to correct english sentences'''
        references.append(line)
        if i%100 == 0:
            sys.stderr.write(".")

    sys.stderr.write("\nReading ndests")
    for j,line in enumerate(open(opts.nbest)):
        (i, sentence, features) = line.strip().split("|||")
        i = int(i)
        stats = list(bleu_stats(sentence, references[i]))
        bleu_score = bleu(stats)
        smoothed_bleu_score = smoothed_bleu(stats)
        # making the feature string to float list
        feature_list = [float(x) for x in features.split()]
        if len(nbests)<=i:
            nbests.append([])
        nbests[i].append(entry(sentence, bleu_score, smoothed_bleu_score, feature_list))
        if j%5000 == 0:
            sys.stderr.write(".")

    arg_num = len(nbests[0][0].feature_list)
    theta = [1.0/arg_num for _ in xrange(arg_num)] #initialization

    sys.stderr.write("\nTraining...\n")
    for i in xrange(opts.epo):
        mistake = 0;
        for nbest in nbests:
            sample = get_sample(nbest)
            sample.sort(key=lambda i: i[0].smoothed_bleu - i[1].smoothed_bleu, reverse=True)
            for i in xrange(min(len(sample), opts.xi)):
                v1 = sample[i][0].feature_list
                v2 = sample[i][1].feature_list
                if dot_product(theta, v1) <= dot_product(theta, v2):
                    mistake += 1
                    theta = vector_plus(theta, vector_plus(v1, v2, -1), opts.eta)
        sys.stderr.write("Mistake:  %s\n" % (mistake,))
    avg_theta = avg_theta / avg_cnt
    print "\n".join([str(weight) for weight in avg_theta])

if __name__ == '__main__':
    main()
