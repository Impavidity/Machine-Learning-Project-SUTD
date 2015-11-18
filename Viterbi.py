# -*-coding: utf-8 -*-

import json
from EmissionEstimate import *

def TransitionEstimate(TagSet, tagList):
	TransitionParameter = {}
	TagSet = ["start"] + TagSet + ["stop"]
	for tag_1 in TagSet:
		TransitionParameter[tag_1] = {}
		for tag_2 in TagSet:
			TransitionParameter[tag_1][tag_2] = 0
	for sentenceTag in tagList:
		sentenceLength = len(sentenceTag)
		TransitionParameter['start'][sentenceTag[0]] += 1
		for i in range(sentenceLength-1):
			TransitionParameter[sentenceTag[i]][sentenceTag[i+1]] += 1
		TransitionParameter[sentenceTag[sentenceLength-1]]['stop'] += 1
	for key_1 in TransitionParameter.keys():
		Count = 0
		for key_2 in TransitionParameter[key_1].keys():
			Count += TransitionParameter[key_1][key_2]
		for key_2 in TransitionParameter[key_1].keys():
			if TransitionParameter[key_1][key_2] == 0:
				TransitionParameter[key_1][key_2] = 0
			else:
				TransitionParameter[key_1][key_2] = float(TransitionParameter[key_1][key_2])/float(Count)*100
	#print json.dumps(TransitionParameter, indent = 4)
	return TransitionParameter

def Filter(v):
	if v is None:
		return 0
	else:
		return v

def BackTrack(AnsList,sentence):
	#print sentence
	#print json.dumps(AnsList,indent=4)
	length = len(AnsList)
	#print length
#	if 'stop' in AnsList[length-1]:
	PredictiveTagForSentence = [AnsList[length-1]['stop']]
#	else:
#		print sentence
#		print json.dumps(AnsList,indent=4)
	for i in range(length-2):
		PredictiveTagForSentence = [AnsList[length-2-i][PredictiveTagForSentence[0]]] + PredictiveTagForSentence
	#print PredictiveTagForSentence
	return PredictiveTagForSentence
		
	#print json.dumps(AnsList, indent= 4)
	#print sentence



def ViterbiDP(TagSet, TransitionParameter, FixedParameter, TestSentence, MainTag):
	PredictiveTag = []
	for sentence in TestSentence:
		sentenceLength = len(sentence)
		f = []
		AnsList = []
		for state in range(sentenceLength):
			f.append({})
			AnsList.append({})
			if state == 0:
				for tag in TagSet:
					f[0][tag] = TransitionParameter['start'][tag]*Filter(FixedParameter[tag].get(sentence[0]))
					AnsList[0][tag] = "start"
			else:
				for tag_2 in TagSet:
					f[state][tag_2] = 0
					AnsList[state][tag_2] = MainTag
					for tag_1 in TagSet:
						Current = f[state-1][tag_1]*TransitionParameter[tag_1][tag_2]*Filter(FixedParameter[tag_2].get(sentence[state]))
						if Current > f[state][tag_2]:
							f[state][tag_2] = Current
							AnsList[state][tag_2] = tag_1

		Score = 0
		AnsList.append({'stop':MainTag})
		for tag in TagSet:
			c = f[sentenceLength-1][tag]*TransitionParameter[tag]['stop']
			if c > Score:
				Score = c
				AnsList[sentenceLength]['stop'] = tag
		
		PredictiveTagForSentence = BackTrack(AnsList,sentence)

		PredictiveTag.append(PredictiveTagForSentence)
	return PredictiveTag




def Test(TagSet, TransitionParameter, FixedParameter, TestSentence, AnsTag, MainTag):
	PredictiveTag =  ViterbiDP(TagSet, TransitionParameter, FixedParameter, TestSentence, MainTag)
	if AnsTag is None:
		print "AnsTag is None"
	if PredictiveTag is None:
		print "PredictiveTag is None"
	Accuracy = AccuracyCalc(PredictiveTag, AnsTag)
	return PredictiveTag, Accuracy


def CheckFixedParameter(FixedParameter,TestSentence):
	for sentence in TestSentence:
		for word in sentence:
			count = 0
			for tag in FixedParameter.keys():
				if word in FixedParameter[tag]:
					count += 1
			if count == 0:
				print word


def main():
	
	wordList, tagList = FileProcess("NPC/train")
	TagDict, CountEmission, TagSet = EmissionProbabilityCalc(wordList, tagList)
	TransitionParameter = TransitionEstimate(TagSet, tagList)
	TestSentence = GetTestSentence(TestFile="NPC/dev.in")
	FixedParameter = FixedParameterCalc(TagDict, CountEmission, TestSentence)
	#CheckFixedParameter(FixedParameter,TestSentence)
	AnsTag = GetAns(CheckFile="NPC/dev.out")
	PredictiveTag,Accuracy = Test(TagSet,TransitionParameter,FixedParameter,TestSentence,AnsTag, MainTag = "O")
	WriteAns(TestSentence,PredictiveTag,"NPC/dev.p3.out")
	print Accuracy
	
	wordList, tagList = FileProcess("POS/train")
	TagDict, CountEmission, TagSet = EmissionProbabilityCalc(wordList, tagList)
	TransitionParameter = TransitionEstimate(TagSet, tagList)
	TestSentence = GetTestSentence(TestFile="POS/dev.in")
	FixedParameter = FixedParameterCalc(TagDict, CountEmission, TestSentence)
	AnsTag = GetAns(CheckFile="POS/dev.out")
	PredictiveTag,Accuracy = Test(TagSet,TransitionParameter,FixedParameter,TestSentence,AnsTag, MainTag="IN")
	WriteAns(TestSentence,PredictiveTag,"POS/dev.p3.out")
	print Accuracy

if __name__=="__main__":
	main()