'''
This is the part 2 of the project:
Emission Estimation
'''
# -*-coding: utf-8 -*-
import json

class WordWithTag(object):
    '''This is the class for each word with tag'''
    def __init__(self, word, tag):
        self.__word = word
        self.__tag = tag

    def set_tag(self, tag):
        '''Set the tag'''
        self.__tag = tag

    def get_word(self):
        '''Get the word'''
        return self.__word

    def get_tag(self):
        '''Get the tag'''
        return self.__tag

    def get_pair(self):
        '''Get word tag pair'''
        return [self.__word, self.__tag]

class Sentence(object):
    '''This is the class for each sentence'''
    def __init__(self):
        self.__sentence = []
        self.__length = 0

    def add_word_tag_pair(self, word):
        '''add word to the sentence'''
        self.__sentence.append(word)
        self.__length += 1

    def get_sentence(self):
        '''Get the word-tag pair list'''
        return [item.get_pair() for item in self.__sentence]

    def get_word_list(self):
        '''Get word list'''
        return [item.get_word() for item in self.__sentence]

    def get_tag_list(self):
        '''Get tag list'''
        return [item.get_tag() for item in self.__sentence]

    def get_length(self):
        '''Get the length of sentence'''
        return self.__length

    def __getitem__(self, i):
        return self.__sentence[i]


class EmissionEstimate(object):
    '''This is the class for emission estimate'''
    def __init__(self):
        self.__train_file = None
        self.__corpus_list = []
        self.__corpus_list_new = None
        self.tag_dict = {}
        self.word_dict = {}
        self.__test_result = None

    @classmethod
    def __data_format_check(cls, file_dir):
        '''
        This function is for checking
        the training data format to see
        there is a space in the word
        '''
        file_read = open(file_dir, "r")
        line_num = 0
        tag = True
        for line in file_read.readlines():
            if line == "\n":
                line_num += 1
                continue
            line_num += 1
            length = len(line.strip().split(" "))
            if length != 2:
                print "[FORMAT]", line_num, ":", line
                tag = False
        return tag

    @classmethod
    def word_process(cls, word):
        '''Lowercase the word'''
        return word.lower()

    def __file_process(self, file_dir, word_process_flag):
        '''File process'''
        try:
            file_read = open(file_dir, "r")
            sentence = Sentence()
            self.__corpus_list_new = []
            for line in file_read.readlines():
                if len(line.strip().split(" ")) == 2:
                    if word_process_flag:
                        word = self.word_process(line.strip().split(" ")[0])
                    else:
                        word = line.strip().split(" ")[0]
                    tag = line.strip().split(" ")[1]
                    self.tag_dict[tag] = self.tag_dict.get(tag,0) + 1
                    # save the corpus for further use
                    item = WordWithTag(word, tag)
                    sentence.add_word_tag_pair(item)
                    # add the word-tag into parameter
                    self.__add_word(word,tag)
                else:
                    self.__corpus_list_new.append(sentence)
                    sentence = Sentence()
            self.__corpus_list += self.__corpus_list_new
        except Exception, error:
            print "[FILE] Read", file_dir, "Error:", error
            exit(0)
        else:
            print "[CORPUS] add corpus successfully!"
        finally:
            if file_read:
                file_read.close()

    def __add_word(self, word, tag):
        '''Use the corpus to train the parameter'''
        poss_tag_dict = self.word_dict.get(word,{})
        poss_tag_dict[tag] = poss_tag_dict.get(tag,0) + 1
        self.word_dict[word] = poss_tag_dict
        

    def add_corpus(self, file_dir, word_process_flag=True):
        '''Add the corpus to the original model'''
        print "[FILE] Check the file format ..."
        if self.__data_format_check(file_dir):
            print "[FILE] Check the file format successfully!"
        else:
            exit(0)
        self.__file_process(file_dir, word_process_flag)
    

    def get_corpus_list(self, para="total"):
        '''Get the corpus list'''
        # you can choose get the new corpus or total corpus
        if para == "total":
            return [sentence.get_sentence() for sentence in self.__corpus_list]
        else:
            return [sentence.get_sentence() for sentence in self.__corpus_list_new]

    def get_corpus_tag(self, para="total"):
        '''Get the corpus tag'''
        # you can choose get the new corpus or total corpus
        if para == "total":    
            return [sentence.get_tag_list() for sentence in self.__corpus_list]
        else:
            return [sentence.get_tag_list() for sentence in self.__corpus_list_new]
    def get_corpus_word(self, para="total"):
        '''Get the corpus tag'''
        # you can choose get the new corpus or total corpus
        if para == "total":
            return [sentence.get_word_list() for sentence in self.__corpus_list]
        else:
            return [sentence.get_word_list() for sentence in self.__corpus_list_new]
    def __predict(self, word):
        try:
            prob = 0
            ans = None
            if word in self.word_dict:
                for tag_option in self.word_dict[word]:
                    current_prob = float(self.word_dict[word][tag_option]) \
                    /float(self.tag_dict[tag_option]+1)
                    if prob < current_prob:
                        prob = current_prob
                        ans = tag_option
            else:
                for tag_option in self.tag_dict:
                    current_prob = 1.0/float(self.tag_dict[tag_option]+1)
                    if prob < current_prob:
                        prob = current_prob
                        ans = tag_option
            return ans
        except Exception, error:
            print "[PREDICT] predict error:", e 

    def test(self, file_dir, ans_dir, word_process_flag=True):
        '''Test'''
        print "[TEST] Test begins ..."
        try:
            test_file = open(file_dir, "r")
            ans_file = open(ans_dir, "w")
            self.__test_result = []
            sentence = Sentence()
            for line in test_file.readlines():
                if line != "\n":
                    if word_process_flag:
                        word = self.word_process(line.strip())
                    else:
                        word = line.strip()
                    original_word = line.strip()
                    tag = self.__predict(word)
                    ans_file.write(original_word+" "+tag+"\n")
                    item = WordWithTag(word,tag)
                    sentence.add_word_tag_pair(item)
                else:
                    ans_file.write("\n")
                    self.__test_result.append(sentence)
                    sentence = Sentence()
        except IOError,error:
            print "[FILE] Test file IO failed:",error
            exit(0)
        else:
            print "[TEST] Test finished!"
        finally:
            if test_file:
                test_file.close()
            if ans_file:
                ans_file.close()

    def get_test_list(self):
        '''Get the test ans list'''
        return [sentence.get_sentence() for sentence in self.__test_result]

    def accuracy_calc(self, ans_file, gold_ans_file):
        right = 0
        total = 0
        try:
            ans_file_read = open(ans_file, "r")
            gold_ans_file_read = open(gold_ans_file, "r")
            ans = ans_file_read.readlines()
            gold_ans = gold_ans_file_read.readlines()
            while gold_ans[-1] == "\n":
                gold_ans.pop()
            while ans[-1] == "\n":
                ans.pop()
            if len(ans) != len(gold_ans):
                print "[FILE] Two answer files' length error"
                exit(0)
            for i in range(len(ans)):
                if ans[i] == "\n" or gold_ans[i] == "\n":
                    continue
                if ans[i] == gold_ans[i]:
                    right += 1
                total += 1
            print "[TEST] Model test accuracy:",float(right)/float(total)
            return float(right)/float(total)
        except IOError, error:
            print "[FILE] Answer file IO error:", error
        finally:
            if ans_file_read:
                ans_file_read.close()
            if gold_ans_file_read:
                gold_ans_file_read.close()





def main():
    '''Model Test'''
    model_for_POS = EmissionEstimate()
    model_for_POS.add_corpus("POS/train")
    model_for_POS.test("POS/dev.in","POS/dev.p2.out")
    model_for_POS.accuracy_calc("POS/dev.p2.out","POS/dev.out")

    model_for_NPC = EmissionEstimate()
    model_for_NPC.add_corpus("NPC/train")
    model_for_NPC.test("NPC/dev.in","NPC/dev.p2.out")
    model_for_NPC.accuracy_calc("NPC/dev.p2.out","NPC/dev.out")


if __name__ == "__main__":
    main()
