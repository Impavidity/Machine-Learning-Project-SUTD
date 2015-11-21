'''
This is the part 3 of the project:
Transition Estimation
'''
# -*-coding: utf-8 -*-
import json
from emission import *

class TransitionEstimate(EmissionEstimate):
	'''This is the class for transition estimate'''
	def __init__(self):
		EmissionEstimate.__init__(self)
		self.transition_para = None
		self.transition_origin_tag_count = None
		self.tag_set = None
		self.__main_tag = None
		
	def __transition_para_calc(self, corpus_tag_list):
		'''Calculate the transition parameter'''
		# the transition_para initial
		# make it support add_corpus
		if not self.transition_para and not self.transition_origin_tag_count:
			self.transition_para = {}
			for tag_1 in self.tag_set:
				self.transition_para[tag_1] = {}
				for tag_2 in self.tag_set:
					self.transition_para[tag_1][tag_2] = 0
			self.transition_origin_tag_count = {}
			for tag in self.tag_set:
				self.transition_origin_tag_count[tag] = 0
		# transition parameter calculate
		for tag_list in corpus_tag_list:
			length = len(tag_list)
			self.transition_para['start'][tag_list[0]] += 1
			self.transition_origin_tag_count['start'] += 1
			for i in range(length-1):
				tag_1 = tag_list[i]
				tag_2 = tag_list[i+1]
				self.transition_para[tag_1][tag_2] += 1
				self.transition_origin_tag_count[tag_1] += 1
			self.transition_para[tag_list[length-1]]['stop'] += 1
			self.transition_origin_tag_count[tag_list[length-1]] += 1

	def add_corpus(self, file_dir, word_process_flag=True):
		'''count the emission and transition parameter'''
		EmissionEstimate.add_corpus(self, file_dir, word_process_flag)
		self.tag_set = ["start"] + self.tag_dict.keys() + ["stop"]
		corpus_tag_list = self.get_corpus_tag(para="new")
		if not corpus_tag_list:
			print "[ERROR] Get corpus tag list error!"
		else:
			self.__transition_para_calc(corpus_tag_list)

	def __get_trans_para(self, tag1, tag2):
		'''get the transition parameter from tag1 to tag2'''
		if self.transition_para[tag1][tag2] == 0:
			return 0
		return float(self.transition_para[tag1][tag2]) \
			/ float(self.transition_origin_tag_count[tag1])

	def __get_emission_para(self, tag, word, word_process_flag):
		'''get the emission parameter from tag to word'''
		if word_process_flag:
			word = self.word_process(word)
		if word in self.word_dict:
			return float(self.word_dict[word].get(tag, 0)) \
				/ float(self.tag_dict.get(tag,0)+1)
		else:
			return 1.0/float(self.tag_dict.get(tag,0)+1)

	def __backtrack(self, ans_list):
		length = len(ans_list)
		tag_for_sentence = [ans_list[length-1]['stop']]
		for i in range(length-2):
			tag_for_sentence = [ans_list[length-2-i][tag_for_sentence[0]]] \
				+ tag_for_sentence
		return tag_for_sentence

	def __get_main_tag(self):
		tag = ""
		num = 0
		for item in self.tag_dict:
			if self.tag_dict[item] > num:
				tag = item
				num = self.tag_dict[item]
		return tag

	def __viterbi_DP(self, ans_file, word_process_flag):
		self.__main_tag = self.__get_main_tag()
		'''DP viterbi algorithm'''
		for sentence in self.__test_result:
			f = []
			ans_list = []
			length = sentence.get_length()
			for state in range(length):
				f.append({})
				ans_list.append({})
				if state == 0:
					for tag in self.tag_set:
						f[state][tag] = self.__get_trans_para("start",tag) \
							* self.__get_emission_para(tag, 
												sentence[state].get_word(),
												word_process_flag)
				else:
					for tag2 in self.tag_set:
						f[state][tag2] = 0
						ans_list[state][tag2] = self.__main_tag
						for tag1 in self.tag_set:
							current = f[state-1][tag1] * self.__get_trans_para(tag1, tag2) \
								* self.__get_emission_para(tag2, 
													sentence[state].get_word(),
													word_process_flag)
							if current > f[state][tag2]:
								f[state][tag2] = current
								ans_list[state][tag2] = tag1
			score = 0
			ans_list.append({'stop':self.__main_tag})
			for tag in self.tag_set:
				c = f[-1][tag] * self.__get_trans_para(tag, "stop")
				if c > score:
					score = c
					ans_list[-1]['stop'] = tag

			tag_for_sentence = self.__backtrack(ans_list)
			for i in range(sentence.get_length()):
				sentence[i].set_tag(tag_for_sentence[i])
				ans_file.write(sentence[i].get_word()+" "+sentence[i].get_tag()+'\n')
			ans_file.write("\n")



	def test(self, test_dir, ans_dir, word_process_flag=True):
		'''Use the viterbi DP for test'''
		print "[TEST] Test begins ..."
		try:
			test_file = open(test_dir, "r")
			ans_file = open(ans_dir, "w")
			self.__test_result = []
			sentence = Sentence()
			for line in test_file.readlines():
				if line != "\n":
					original_word = line.strip()
					item = WordWithTag(original_word,"")
					sentence.add_word_tag_pair(item)
				else:
					self.__test_result.append(sentence)
					sentence = Sentence()
			self.__viterbi_DP(ans_file, word_process_flag)

			

		except IOError, error:
			print "[FILE] Test file IO faild:", error
		else:
			print "[TEST] Test finished!"
		finally:
			if test_file:
				test_file.close()
			if ans_file:
				ans_file.close()


def main():
	'''Model Test'''
	model_for_POS = TransitionEstimate()
	model_for_POS.add_corpus("POS/train")
	model_for_POS.test("POS/dev.in","POS/dev.p3.out")
	model_for_POS.accuracy_calc("POS/dev.p3.out","POS/dev.out")


	model_for_POS = TransitionEstimate()
	model_for_POS.add_corpus("NPC/train")
	model_for_POS.test("NPC/dev.in","NPC/dev.p3.out")
	model_for_POS.accuracy_calc("NPC/dev.p3.out","NPC/dev.out")
if __name__ == "__main__":
	main()