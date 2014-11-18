#!/usr/bin/env python
import optparse, sys, os
from collections import namedtuple, defaultdict


def untranslatedWords(f, e):
    count = 0
    for word in e.split():
        if word in f:
            count += 1
    return count



def countWord(word, e):
    count = 0
    for w in e.split():
        if w == word:
            count += 1
    return count



def pre_process(frFileName, nBestFileName):
    newlines = []
    frenches = []
    
    for line in file(frFileName):
        frenches.append(line)

    nBestFile = open(nBestFileName, 'r')
    lastI = 0
    curLines = []
    e_counts = {}
    for line in nBestFile:
        # print line
        (i, sentence, features) = line.strip().split("|||")
        if i == lastI:
            curLines.append(line)
            for word in sentence.split():
                e_counts[word] = e_counts[word]+1 if word in e_counts else 1
        else:
            lastI = i

            for inLine in curLines
            lastI = i
            curLines = []
            e_counts = {}

        feature_list = [x for x in features.split()]
        if len(feature_list) == 6:
            feature_list.append(str(len(sentence.split())))
            feature_list.append(str(untranslatedWords(frenches[int(i)], sentence)))
        else:
            sys.stderr.write('Original feature number is not 6, so the nbest file is not updated\n')
            return
        newlines.append(i + '|||' + sentence + '||| ' + ' '.join(feature_list) + '\n')
    nBestFile.close()
    
    # print newlines
    nBestFile = open(nBestFileName, 'w')
    nBestFile.writelines(newlines)
    nBestFile.close()



def read_ds_from_file(filename):
    import pickle
    pfile = None
    try:
        pfile = open(filename, 'rb')
    except:
        dataStructure = None
    try:
        dataStructure = pickle.load(pfile)
    except:
        dataStructure = None
    if pfile is not None:
        pfile.close()
    return dataStructure

def write_ds_to_file(dataStructure, filename):
    import pickle
    output = open(filename, 'wb')
    pickle.dump(dataStructure, output)
    output.close()



if __name__ == '__main__':
   pre_process('./data/test.fr', './data/test.nbest')

