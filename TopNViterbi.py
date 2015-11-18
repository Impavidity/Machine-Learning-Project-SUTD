# -*-coding: utf-8 -*-

import json
from EmissionEstimate import *
from Viterbi import *

def Insert(CurrentAnsQueue, Current, tag, Seq, topN):
	pos = -1
	#print CurrentAnsQueue
	for i in range(len(CurrentAnsQueue)):

		if Current>CurrentAnsQueue[i].keys()[0]:
			#print Current,CurrentAnsQueue[i].keys()[0]
			pos = i
			break
		if i > topN:
			return CurrentAnsQueue
	if pos == -1:
		pos = len(CurrentAnsQueue)

	CurrentAnsQueue.insert(pos,{Current:(tag,Seq)})
	#print CurrentAnsQueue
	return CurrentAnsQueue

def AnsCheck(PredictiveTagForSentence):
	topN = len(PredictiveTagForSentence)
	'''
	for i in range(topN):
		for j in range(len(PredictiveTagForSentence[i])):
			PredictiveTagForSentence[i][j] = PredictiveTagForSentence[i][j][0]
	'''
	#print PredictiveTagForSentence
	for i in range(topN):
		for j in range(topN):
			if i<j:
				if PredictiveTagForSentence[i] == PredictiveTagForSentence[j]:
					print i,j
					print PredictiveTagForSentence[i]
					print PredictiveTagForSentence[j]

					return False
	return True


def TopNBackTrack(AnsList, sentence):
	#print sentence
	#print json.dumps(AnsList, indent=4)
	
	PredictiveTagForSentence = []
	length = len(AnsList)
	topN = len(AnsList[-1]['stop'])
	for i in range(topN):
		PredictiveTagForSentence.append([AnsList[-1]['stop'][i]])
	for i in range(length-2):
		for j in range(topN):
			PredictiveTagForSentence[j].insert(0,AnsList[length-2-i][PredictiveTagForSentence[j][0][0]][PredictiveTagForSentence[j][0][1]])
	#print "Anscheck:",AnsCheck(PredictiveTagForSentence)
	return PredictiveTagForSentence

def GetTopNTag(TagSet, TransitionParameter, FixedParameter, TestSentence, MainTag, topN):
	PredictiveTag = []
	print "Total sentence = ", len(TestSentence)
	Count = 0
	for sentence in TestSentence:
		print "Now: ",Count
		Count += 1
		sentenceLength = len(sentence)
		f = []
		AnsList = []
		for state in range(sentenceLength):
			f.append({})
			AnsList.append({})
			if state == 0:
				for tag in TagSet:
					f[0][tag] = [TransitionParameter['start'][tag]*Filter(FixedParameter[tag].get(sentence[0]))]
					AnsList[0][tag] = ["start"]
			else:
				for tag_2 in TagSet:
					
					CurrentAnsQueue = []
					'''
					Pointer = {}
					for item in TagSet:
						Pointer[item] = 0
					for i in range(topN):
						for item in tagSet:
					'''

					
					for tag_1 in TagSet:
						Seq = 0
						for item in f[state-1][tag_1]:
							Current = item * TransitionParameter[tag_1][tag_2] * Filter(FixedParameter[tag_2].get(sentence[state]))
							CurrentAnsQueue = Insert(CurrentAnsQueue, Current, tag_1, Seq, topN)
							Seq += 1
					
					#print CurrentAnsQueue
					f[state][tag_2] = []
					AnsList[state][tag_2] = []
					for i in range(min(len(CurrentAnsQueue), topN)):
						f[state][tag_2].append(CurrentAnsQueue[i].keys()[0])
						AnsList[state][tag_2].append(CurrentAnsQueue[i].values()[0])
				
		f.append({})
		AnsList.append({})
		CurrentAnsQueue = []
		for tag in TagSet:
			Seq = 0
			for item in f[sentenceLength-1][tag]:
				Current = item * TransitionParameter[tag]['stop']
				CurrentAnsQueue = Insert(CurrentAnsQueue, Current, tag, Seq, topN)
				Seq += 1
		f[sentenceLength]['stop'] = []
		AnsList[sentenceLength]['stop'] = []
		for i in range(min(len(CurrentAnsQueue), topN)):
			f[sentenceLength]['stop'].append(CurrentAnsQueue[i].keys()[0])
			AnsList[sentenceLength]['stop'].append(CurrentAnsQueue[i].values()[0])
		PredictiveTagForSentence = TopNBackTrack(AnsList, sentence)
		PredictiveTag.append(PredictiveTagForSentence)
		#print json.dumps(f,indent=4)
		#print PredictiveTagForSentence
		#break
	#print PredictiveTag
	return PredictiveTag

def AnsOutput(PredictiveTag, TestSentence, AnsFile):
	AnsFileWrite = open(AnsFile, "w")
	if len(PredictiveTag) != len(TestSentence):
		print "sentence Num error"
	Num = len(PredictiveTag)
	#print "Num",Num
	topN = len(PredictiveTag[0])
	#print "TopN",topN
	for i in range(Num):
		if len(TestSentence[i]) != len(PredictiveTag[i][0]):
			print "Sentence Length Error", i
			return 
		SentenceLength = len(TestSentence[i])
		for j in range(SentenceLength):
			AnsFileWrite.write(TestSentence[i][j])
			for k in range(topN):
				AnsFileWrite.write(" "+PredictiveTag[i][k][j][0])
			AnsFileWrite.write("\n")
		AnsFileWrite.write("\n")
	return




def main():
	wordList, tagList = FileProcess("POS/train")
	
	TagDict, CountEmission, TagSet = EmissionProbabilityCalc(wordList, tagList)
	
	TransitionParameter = TransitionEstimate(TagSet, tagList)
	TestSentence = GetTestSentence(TestFile="POS/dev.in")
	FixedParameter = FixedParameterCalc(TagDict, CountEmission, TestSentence)
	
	PredictiveTag = GetTopNTag(TagSet,TransitionParameter,FixedParameter,TestSentence, MainTag="IN",topN = 10)

	AnsOutput(PredictiveTag,TestSentence,"POS/dev.p4.out")
	
if __name__=="__main__":
	main()