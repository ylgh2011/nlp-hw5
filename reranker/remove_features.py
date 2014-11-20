

input_features_fileName = 'data/test.ibm1_ibm2.nbest'
output_features_fileName = 'data/test.ibm2.nbest'
indexes_to_be_removed = [-2]


for i, x in enumerate(indexes_to_be_removed):
	if x < 0:
		indexes_to_be_removed[i] = len(indexes_to_be_removed) + x

indexes_to_be_removed = list(set(indexes_to_be_removed))
indexes_to_be_removed.sort(reverse=True)

newlines = []
for j,line in enumerate(file(input_features_fileName)):
    (i, sentence, features) = line.strip().split("|||")
    feature_list = [x for x in features.strip().split()]
    for x in indexes_to_be_removed:
    	del(feature_list[x])
    newlines.append(i + '|||' + sentence + '||| ' + ' '.join(feature_list) + '\n')
 
nBestFile = open(output_features_fileName, 'wb')
nBestFile.writelines(newlines)
nBestFile.close()
