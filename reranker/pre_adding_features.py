#!/usr/bin/env python
import optparse, sys, os
from collections import namedtuple, defaultdict


def untranslatedWords(f, e):
	count = 0
	for word in e.split():
		if word in f:
			count += 1
	return count



def pre_process(frFileName, nBestFileName):
	newlines = []
	frenches = []
	
	for line in file(frFileName):
		frenches.append(line)

	nBestFile = open(nBestFileName, 'r')
	for line in nBestFile:
		# print line
		(i, sentence, features) = line.strip().split("|||")
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


if __name__ == '__main__':
   pre_process('./data/test.fr', './data/test.nbest')

