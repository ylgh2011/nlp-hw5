#!/usr/bin/env python
import optparse, sys, os
from collections import namedtuple, defaultdict
# from bleu import bleu_stats, bleu, smoothed_bleu
import bleu
from operator import itemgetter
import itertools
import random
from math import fabs
from library import pre_process
from library import read_ds_from_file
from library import write_ds_to_file



optparser = optparse.OptionParser()
optparser.add_option("-n", "--nbest", dest="nbest", default=os.path.join("data", "train.nbest"), help="N-best file")
optparser.add_option("--en", dest="en", default=os.path.join("data", "train.en"), help="target language references for learning how to rank the n-best list")
optparser.add_option("-t", "--tau", dest="tau", type="float", default=1.0, help="margin size(default 1.0)")

optparser.add_option("-e", "--eta", dest="eta", type="float", default=1, help="perceptron learning rate (default 0.1)")
optparser.add_option("-p", "--epo", dest="epo", type="int",default=5, help="number of epochs for perceptron training (default 5)")

optparser.add_option("-r", "--top_r", dest="r", type="int", default=0.1, help="top r percent scores filter (default 50)")
optparser.add_option("-k", "--bottom_k", dest="k", type="int", default=0.1, help="bottom k percent scores filter (default 50)")

optparser.add_option("--fr", dest="fr", default=os.path.join("data", "train.fr"), help="train French file")
optparser.add_option("--testnbest", dest="testnbest", default=os.path.join("data", "test.nbest"), help="test N-best file")
optparser.add_option("--testfr", dest="testfr", default=os.path.join("data", "test.fr"), help="test French file")
optparser.add_option("--nbestDic", dest="nbestDS", default=os.path.join("data", "nbest.ds.gz"), help="dumping file of the data structure that storing scores for nbestDic")
optparser.add_option("--testen", dest="testen", default=os.path.join("data", "test.en"), help="test en")

(opts, _) = optparser.parse_args()
# entry = namedtuple("entry", "sentence, bleu_score, smoothed_bleu, feature_list")
entry = namedtuple("entry", "sentence, smoothed_bleu, feature_list")

pre_process( [(opts.fr, opts.nbest, opts.en), (opts.testfr, opts.testnbest, opts.testen)] )

def dot_product(l1, l2):
    if (len(l1) != len(l2)):
        raise(ValueError, "product of dif length of vectors")
    ans = 0.0
    for i in xrange(len(l1)):
        ans += l1[i] * l2[i]
    return ans

def scale_product(l1, l2):
    # if ( type(l1) != type(int) and type(l1) != type(float)):
    #     raise(ValueError, "first variable should be a scalar")
    ans = [0 for _ in xrange(len(l2))]
    for i in xrange(len(l2)):
        ans[i] = l1 * l2[i]
    return ans

def vector_plus(v1, v2, multiply=1):
    ans = []
    for i in xrange(len(v1)):
        ans.append(v1[i] + multiply * v2[i])
    return ans


def main():
    references = []
    sys.stderr.write("Reading English Sentences\n")
    for i, line in enumerate(open(opts.en)):
        '''Initialize references to correct english sentences'''
        references.append(line)
        if i%100 == 0:
            sys.stderr.write(".")

    sys.stderr.write("\nTry reading %s from disk ... \n" % opts.nbestDS)
    nbests = read_ds_from_file(opts.nbestDS)
    if nbests is None:
        nbests = []
        sys.stderr.write("%s is not on disk, so calculating it ... \n" % opts.nbestDS)
        for j,line in enumerate(open(opts.nbest)):
            (i, sentence, features) = line.strip().split("|||")
            i = int(i)
            stats = list(bleu.bleu_stats(sentence, references[i]))
            # bleu_score = bleu.bleu(stats)
            smoothed_bleu_score = bleu.smoothed_bleu(stats)
            # making the feature string to float list
            feature_list = [float(x) for x in features.split()]
            if len(nbests)<=i:
                nbests.append([])
            # nbests[i].append(entry(sentence, bleu_score, smoothed_bleu_score, feature_list))
            nbests[i].append(entry(sentence, smoothed_bleu_score, feature_list))

            if j%5000 == 0:
                sys.stderr.write(".")
        sys.stderr.write("\nWriting %s to disk ... \n" % opts.nbestDS)
        write_ds_to_file(nbests, opts.nbestDS)
        sys.stderr.write("Finish writing %s\n" % opts.nbestDS)

    arg_num = len(nbests[0][0].feature_list)
    theta = [1.0/arg_num for _ in xrange(arg_num)] #initialization

    # avg_theta = [ 0.0 for _ in xrange(arg_num)]
    # avg_cnt = 0

    tau = opts.tau # positive learning margin
    sys.stderr.write("\nTraining...\n")
    for iter_num in xrange(opts.epo):
        sys.stderr.write("\nIteration#{} ".format(iter_num + 1))
        cnt = 0;
        # sentence wise updating

        for i, nbest in enumerate(nbests):
            y = sorted(nbest, key = lambda h: h.smoothed_bleu, reverse = True)
            mu = [0.0]*len(nbest)
            w_times_x = [0.0]*len(nbest)
            for j, best in enumerate(nbest):
                # calculate linear function result
                w_times_x[j] = dot_product(theta, best.feature_list)

            # processing pairs 
            top_r = int(len(y)*opts.r)
            bottom_k = int(len(y)*opts.k)
            for j in xrange(len(nbest) - 1):
                for l in xrange(j+1, len(nbest)):
                    if nbest[j].smoothed_bleu <= y[top_r].smoothed_bleu \
                    and nbest[l].smoothed_bleu >= y[- bottom_k].smoothed_bleu \
                    and w_times_x[j] > w_times_x[l] + tau:
                        mu[j] = mu[j] + 1
                        mu[l] = mu[l] - 1
                    elif nbest[j].smoothed_bleu >= y[- bottom_k].smoothed_bleu \
                    and nbest[l].smoothed_bleu <= y[top_r].smoothed_bleu \
                    and w_times_x[j] > w_times_x[l] - tau:
                        mu[j] = mu[j] - 1
                        mu[l] = mu[l] + 1
                    else:
                        cnt += 1
                if j % 10000 == 0:
                    sys.stderr.write(".")

            vector_sum = [0 for _ in xrange(len(nbest[0].feature_list))]
            for m, best in enumerate(nbest):
                vector_sum = vector_plus(vector_sum, scale_product(mu[m], best.feature_list))

            theta = vector_plus(theta, vector_sum, opts.eta)

            # avg_theta = vector_plus(avg_theta, theta)
            # avg_cnt += 1

        sys.stderr.write("\n Non-supported vectors:  %s\n" % (mistake,))
    

    # weights = [ avg / avg_cnt if avg_cnt !=0 else 1/float(arg_num) for avg in avg_theta ]
    sys.stderr.write("Computing best BLEU score and outputing...\n")
    # instead of print the averaged-out weights, print the weights that maximize the BLEU score    
    print "\n".join([str(weight) for weight in theta])

if __name__ == '__main__':
    main()
