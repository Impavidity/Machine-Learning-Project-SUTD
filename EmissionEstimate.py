# -*-coding: utf-8 -*-
import copy
import json

'''
# This function is for checking 
# the training data format to see 
# there is a space in the word

def training_data_format_check(FileDir):
    fr = open(FileDir, "r")
    i = 0
    for line in fr.readlines():
        i += 1
        length = len(line.strip().split(" "))
        if length != 2:
            print i,length,line
'''

def FileProcess(FileDir): 
	try:
		fr = open(FileDir,"r")
		wordList = []
		tagList = []
		words = []
		tags = []
		for line in fr.readlines():
			if len(line.strip().split(" ")) == 2:
				words.append(line.strip().split(" ")[0].lower())
				tags.append(line.strip().split(" ")[1])
			else:
				wordList.append(words)
				tagList.append(tags)
				words = []
				tags = []
		return wordList, tagList
	except IOError, e:
		print "Read",FileDir,"Error:",e
		exit(0)
	else:
		print "Read",FileDir,"Successfully!"
		fr.close()

# Get the tag set, remove the duplicate
def getTags(tagList):
	tag = set([])
	for line in tagList:
		tag = tag | set(line)
	return list(tag)


def EmissionProbabilityCalc(wordList, tagList):
	# Get the tag set
	TagSet = getTags(tagList)
	# Get the number of sentence
	Num = len(wordList)
	# TagDict["tag"] = n means Count(tag) = n
	TagDict = {}
	# CountEmission["tag1"][O] = n means Count[tag1->O] = n
	CountEmission = {}
	for i in range(Num):
		# Get the sentence length
		SentenceLength = len(wordList[i])
		# Count the word number
		for j in range(SentenceLength):
			if tagList[i][j] in TagDict:
				TagDict[tagList[i][j]] += 1
			else:
				TagDict[tagList[i][j]] = 1

			if tagList[i][j] in CountEmission:
				if wordList[i][j] in CountEmission[tagList[i][j]]:
					CountEmission[tagList[i][j]][wordList[i][j]] += 1
				else:
					CountEmission[tagList[i][j]][wordList[i][j]] = 1
			else:
				CountEmission[tagList[i][j]] = {}
				CountEmission[tagList[i][j]][wordList[i][j]] = 1
	return TagDict, CountEmission, TagSet

def ParameterCalc(TagDict, CountEmission):
	parameter = copy.deepcopy(CountEmission)
	for key in TagDict.keys():
		for word in CountEmission[key].keys():
			parameter[key][word] = float(CountEmission[key][word])/float(TagDict[key])
	return parameter


def FixedParameterCalc(TagDict, CountEmission, TestSentence):
	TestEmission = {}
	TagNum = len(TagDict.keys())
	for key in TagDict.keys():
		TestEmission[key] = {}
	CheckedList = {}
	for sentence in TestSentence:
		for word in sentence:
			if word in CheckedList:
				continue
			else:
				CheckedList[word] = True
				Count = 0
				for key in TagDict.keys():
					if word in CountEmission[key]:
						TestEmission[key][word] = float(CountEmission[key][word])/float(TagDict[key]+1)
					else:
						Count += 1
				if Count == TagNum:
					for key in TagDict.keys():
						TestEmission[key][word] = float(1)/float(TagDict[key]+1)
	return TestEmission


def Predict(TestSentence, FixedParameter):
	PredictiveTag = []
	#print FixedParameter["IN"]
	for sentence in TestSentence:
		TagForSentence = []
		for word in sentence:
			tag = ""
			prob = 0
			for key in FixedParameter.keys():
				if word in FixedParameter[key]:
					if FixedParameter[key][word]>prob:
						prob = FixedParameter[key][word]
						tag = key
			TagForSentence.append(tag)
		PredictiveTag.append(TagForSentence)
	return PredictiveTag

def AccuracyCalc(PredictiveTag, AnsTag):
	if len(PredictiveTag) != len(AnsTag):
		print "Sentence Num Wrong!"
		return "Error"
	SentenceNum = len(PredictiveTag)
	Total = 0
	Right = 0
	for senNum in range(SentenceNum):
		try:
			if len(PredictiveTag[senNum]) != len(AnsTag[senNum]):
				print "Sentence Length Wrong:",senNum
				return "Error"
		except:
			print senNum ,"is None"
			print PredictiveTag[senNum]
			print AnsTag[senNum]
		SentenceLength = len(PredictiveTag[senNum])
		Total += SentenceLength
		for tagNum in range(SentenceLength):
			if PredictiveTag[senNum][tagNum] == AnsTag[senNum][tagNum]:
				Right += 1
			else:
				pass
				#print "wrong:",PredictiveTag[senNum][tagNum], AnsTag[senNum][tagNum]
	return float(Right)/float(Total)

def GetTestSentence(TestFile):
	TestFileRead = open(TestFile, "r")
	TestSentence = []
	Words = []
	for line in TestFileRead.readlines():
		if line != "\n":
			Words.append(line.strip().lower())
		else:
			TestSentence.append(Words)
			Words = []
	return TestSentence

def GetAns(CheckFile):
	CheckFileRead = open(CheckFile, "r")
	AnsTag = []
	Tag = []
	for line in CheckFileRead.readlines():
		if line != "\n":
			Tag.append(line.strip().split(" ")[1])
		else:
			AnsTag.append(Tag)
			Tag = []
	return AnsTag

def WriteAns(TestSentence, PredictiveTag, AnsFile):
	AnsFileWrite = open(AnsFile, "w")
	if len(TestSentence) != len(PredictiveTag):
		print "Sentence Num Error"
		return
	Num = len(TestSentence)
	for i in range(Num):
		if len(TestSentence[i])!= len(PredictiveTag[i]):
			print "Sentence Length Error:",i
			return
		SentenceLength = len(TestSentence[i])
		for j in range(SentenceLength):
			AnsFileWrite.write(TestSentence[i][j]+" "+PredictiveTag[i][j]+"\n")
		AnsFileWrite.write("\n")
	return



def TestFace(TagDict, CountEmission, TestFile, AnsFile, CheckFile):
	
	TestSentence = GetTestSentence(TestFile)
	AnsTag = GetAns(CheckFile)

	FixedParameter = FixedParameterCalc(TagDict, CountEmission, TestSentence)
	PredictiveTag = Predict(TestSentence, FixedParameter)
	WriteAns(TestSentence,PredictiveTag,AnsFile)

	Accuracy = AccuracyCalc(PredictiveTag, AnsTag)
	return Accuracy




def main():
	'''
	TrainingDataFormatCheck("NPC/train")
	TrainingDataFormatCheck("POS/train")
	'''
	
	wordList, tagList = FileProcess("NPC/train")
	TagDict, CountEmission, TagSet = EmissionProbabilityCalc(wordList, tagList)
	# The parameter is not used in the test face but just finish a function for the question in the project
	parameter = ParameterCalc(TagDict, CountEmission)
	Accuracy = TestFace(TagDict, CountEmission, "NPC/dev.in", "NPC/dev.p2.out","NPC/dev.out")
	print "The accuracy of NPC:",Accuracy
	#print json.dumps(TagDict, indent=4)
	#print json.dumps(CountEmission,indent=4)
	#print json.dumps(parameter, indent=4)
	

	wordList, tagList = FileProcess("POS/train")
	TagDict, CountEmission, TagSet = EmissionProbabilityCalc(wordList, tagList)
	# The parameter is not used in the test face but just finish a function for the question in the project
	parameter = ParameterCalc(TagDict, CountEmission)
	Accuracy = TestFace(TagDict, CountEmission, "POS/dev.in", "POS/dev.p2_with_lower.out","POS/dev.out")
	print "The accuracy of POS:",Accuracy
	#print json.dumps(TagDict, indent=4)
	#print json.dumps(CountEmission,indent=4)
	#print json.dumps(parameter, indent=4)

		
if __name__=="__main__":
	main()