# written by 
# Joshua Agby
# joshagby


import sys
import os
import preprocess
import math
import operator

# accepted schemes are:
# tfidf / tfidf
# tfc / nfx

# declare globals for easier invIndex access
df = 'df'
docList = 'docList'
idf = 'idf'

# Function that adds a document to the inverted index:
# input: the content of the document (string); 
# input: weighting scheme for documents (string); 
# input: weighting scheme for query (input); 
# input/output: inverted index (your choice of data structure)
def indexDocument(inString, schemeDocs, schemeQuery, invIndex):
	# check scheme
	if schemeDocs == 'tfidf' or schemeDocs == 'tfc':
		# Preprocess input string into list of tokens
		tokenList = preprocess.stemWords((preprocess.removeStopwords((preprocess.tokenizeText(preprocess.removeSGML(inString))))))

		# get document number and increment doc-count
		docNum = invIndex['doc-count']
		invIndex['doc-count'] += 1

		# build temporary dictionary of term frequencies for this document
		# wordDict { 'word': tf }
		wordDict = {}
		for word in tokenList:
			if word in wordDict:
				wordDict[word] += 1.0
			else:
				wordDict[word] = 1.0

		# add entries to invIndex for each word
		# increments document frequency where necessary
		for word, tf in wordDict.iteritems():
			if word in invIndex:
				invIndex[word][docList].append([docNum, tf])
				invIndex[word][df] += 1.0
			else:
				invIndex[word] = {df: 1.0, docList: [[docNum, tf]]}
		return invIndex
	else:
		sys.exit("Document weighting scheme '" + schemeDocs + "' is not acceptable input. Try 'tfidf' or 'tcf'.")

# Function that retrieves information from the index for a given query.
# input: query (string); 
# input: inverted index (your choice of data structure); 
# input: weighting scheme for documents (string); 
# input: weighting scheme for query; 
# output: ids for relevant documents, along with similarity scores (dictionary)
def retrieveDocuments(query, invIndex, schemeDocs, schemeQuery):
	# Preprocess query into list of tokens
	tokenList = preprocess.stemWords((preprocess.removeStopwords((preprocess.tokenizeText(preprocess.removeSGML(query))))))

	# get query term frequencies
	queryTermFreq = {}
	for word in tokenList:
		# only include words that appear in at least one document
		if word in invIndex:
			if word in queryTermFreq:
				queryTermFreq[word] += 1.0
			else:
				queryTermFreq[word] = 1.0

	# get query length, (query term normalization)
	queryLength = 0.0
	for word in queryTermFreq:
		if word in invIndex:
			queryLength += math.pow(invIndex[word][idf] * queryTermFreq[word], 2)
	queryLength = math.sqrt(queryLength)

	# first scheme set is tfidf.tfidf with no normalization
	if schemeQuery == 'tfidf' and schemeDocs == schemeQuery:
		# create similarity score dictionary -> maps relevant docs to similarity score
		# first step is to create the numerator (dot product), then divide all terms by denominator (normalization)
		# using tfc method for query and document
		simScores = {}
		# iterate over each word
		for word in queryTermFreq:
			# and each document that contains that word
			for docNum, tf in invIndex[word][docList]:
				if docNum in simScores:
					simScores[docNum] += (queryTermFreq[word] * tf * math.pow(invIndex[word][idf], 2))
				else:
					simScores[docNum] = (queryTermFreq[word] * tf * math.pow(invIndex[word][idf], 2))

		# divide each dot product by normalization factor -- APARENTLY DO NOT DO THIS?!?!?
		# REMOVED --
		# for doc in simScores:
		# 	simScores[doc] = simScores[doc] / (queryLength * docLengths[doc])

		# return the simScore dictionary
		return simScores

		# create simScoresList
		# simScoresList = []
		# for docNum, score in simScores.iteritems():
		# 	simScoresList.append([docNum, score])
		# simScoresList.sort(key=lambda scores: scores[1], reverse=True)

	# second scheme is tfc.nfx
	elif schemeDocs == 'tfc' and schemeQuery == 'nfx':
		# get max term frequency in query
		queryMaxTF = 0
		for word, tf in queryTermFreq.iteritems():
			if tf > queryMaxTF:
				queryMaxTF = tf

		simScores ={}

		# iterate over each word in query and each doc that contains those words
		for word in queryTermFreq:
			for docNum, tf in invIndex[word][docList]:
				if docNum in simScores:
					simScores[docNum] += (tf * math.pow(invIndex[word][idf], 2) * (0.5 + (0.5 * queryTermFreq[word] / queryMaxTF)))
				else:
					simScores[docNum] = (tf * math.pow(invIndex[word][idf], 2) * (0.5 + (0.5 * queryTermFreq[word] / queryMaxTF)))


		# normalize using document length (tfc scheme for doc)
		for doc in simScores:
			simScores[doc] = simScores[doc] / docLengths[doc]

		return simScores


if __name__ == '__main__':
	schemeDocs = sys.argv[1]
	schemeQuery = sys.argv[2]
	inFolder = sys.argv[3]
	inQueries = sys.argv[4]

	
	invIndex = {}
	# invIndex {
	#	'doc-count': docCounter
	# 	'word1': {'df':numDocsWithWord, 
	# 			  'idf': idfValueForWord,
	# 			  'docList': [[docNum, tf],[docNum2, tf]] } 
	# }

	# temporary invIndex entry to identify documents
	invIndex['doc-count'] = 1

	# Loop through each file, and add document to inverted index
	for filename in os.listdir(inFolder):
		# iterate over each line of the file to create a single string (with no newlines)
		lineStr = ''
		for line in open(inFolder + filename, 'r'):
			lineStr += ' ' + line.rstrip()

		# add document data to inverted index
		invIndex = indexDocument(lineStr, schemeDocs, schemeQuery, invIndex)
	
	totalDocumentCount = float(invIndex['doc-count'] - 1)
	# delete the temporary entry
	del invIndex['doc-count']

	# maps document numbers to document length for nomralization
	docLengths = {}
	
	# generate idf and docLength for all words and documents (respectively)
	# docLength dictionary will contain sum of (tf*idf)^2 vectors for all terms in document
	for word in invIndex:
		# calculate idf value for word
		invIndex[word][idf] = math.log10(totalDocumentCount / invIndex[word][df])
		# calculate document length term for each document that contains the word
		for docNum, tf in invIndex[word][docList]:
			if docNum in docLengths:
				docLengths[docNum] += math.pow(invIndex[word][idf] * tf, 2)
			else:
				docLengths[docNum] = math.pow(invIndex[word][idf] * tf, 2)

	# take sqrt of all docLength terms to get necessary value
	for doc in docLengths:
		docLengths[doc] = math.sqrt(docLengths[doc])

	# build dictionary of queries where query number maps to the query string
	queries = {}
	for line in open(inQueries):
		line.rstrip()
		line = line.split()
		queryNum = int(line[0])
		queries[queryNum] = ' '.join(line[1:])

	# build list of all [query, docNumber, simScore] sets 
	simScoreList = []
	for queryNum, queryStr in queries.iteritems():
		simScoreDict = retrieveDocuments(queryStr, invIndex, schemeDocs, schemeQuery)
		for docNum, simScore in simScoreDict.iteritems():
			simScoreList.append([queryNum, docNum, simScore])

	outfile = open('cranfield.' + schemeDocs + '.' + schemeQuery + '.output', 'w')

	# sort similarity score list such that they are ordered 
	# by querynumber and then similarity score
	simScoreList = sorted(simScoreList, key=operator.itemgetter(2), reverse=True)
	simScoreList = sorted(simScoreList, key=operator.itemgetter(0))

	# write results to output file
	for queryNum, docNum, simScore in simScoreList:
		outfile.write(str(queryNum) + ' ' + str(docNum) + ' ' + str(simScore) + '\n')



	# ---------------------------------------------------------------------------------
	# THE REMAINING CODE WAS USED TO CALCULATE MACRO AVERAGED PRECISION AND RECALL
	# Varied the parameter 'docsPerQuery' and command line input to get all data

	# build reljudge dictionary mapping queryNumber to another dictonary mapping docNumber to nothing
	# reljudge = {}
	# for line in open('cranfield.reljudge', 'r'):
	# 	queryNum = int(line.split()[0])
	# 	doc = int(line.split()[1])
	# 	if queryNum in reljudge:
	# 		reljudge[queryNum][doc] = 1
	# 	else:
	# 		reljudge[queryNum] = {doc: 1}


	# docsPerQuery = 10
	# totalPrecision = 0.0
	# totalRecall = 0.0
	# lastQueryNum = 0
	# docCount = 0
	# isFirst = True
	# for queryNum, docNum, simScore in simScoreList:
	# 	if docCount > docsPerQuery and queryNum == lastQueryNum:
	# 		continue
	# 	if queryNum != lastQueryNum:
	# 		# new query - add precision and recall value to totals
	# 		# and reset all appropriate values
	# 		# also check for relevantNotRetrieved by looking at size of reljudgeTemp
	# 		if not isFirst:
	# 			relevantNotRetrieved = len(reljudgeTemp)
	# 			totalPrecision += (relevantRetrieved / (relevantRetrieved + irrelevantRetrieved))
	# 			totalRecall += (relevantRetrieved / (relevantRetrieved + relevantNotRetrieved))				

	# 		relevantRetrieved = 0.0
	# 		relevantNotRetrieved = 0.0
	# 		irrelevantRetrieved = 0.0
	# 		lastQueryNum = queryNum
	# 		# dictionary of all relevant docs for new query
	# 		reljudgeTemp = reljudge[queryNum]
	# 		isFirst = False
	# 		docCount += 1

	# 	if docNum in reljudgeTemp:
	# 		relevantRetrieved += 1.0
	# 		del reljudgeTemp[docNum]
	# 	else:
	# 		irrelevantRetrieved += 1.0

	# macroAveragedPrecision = totalPrecision / len(queries)
	# macroAveragedRecall = totalRecall / len(queries)

	# print 'Using top ' + str(docsPerQuery) + ' documents in the ranking...'
	# print 'with ' + schemeDocs + '.' + schemeQuery + ' weighting scheme...'
	# print 'Macro averaged recall: ' + str(macroAveragedRecall)
	# print 'Macro averaged precision: ' + str(macroAveragedPrecision)

