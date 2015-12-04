#!/usr/bin/env python
# encoding: utf-8

import os.path

class PinYin(object):
    def __init__(self):
        self.word_dict = {}

    def load_word(self, dict_file):
        self.dict_file = dict_file
        if not os.path.exists(self.dict_file):
            raise IOError("NotFoundFile")

        with file(self.dict_file) as f_obj:
            for f_line in f_obj.readlines():
                try:
                    line = f_line.split('    ')
                    self.word_dict[line[0]] = line[1]
                except:
                    line = f_line.split('   ')
                    self.word_dict[line[0]] = line[1]


    def hanzi2pinyin(self, string="", firstcode=False):
        result = []
        if not isinstance(string, unicode):
            string = string.decode("utf-8")

        for char in string:
            key = '%X' % ord(char)
            value = self.word_dict.get(key, char)
            outpinyin = str(value).split()[0][:-1].lower()
            if not outpinyin:
                outpinyin = char
            if firstcode:
                result.append(outpinyin[0])
            else:
                result.append(outpinyin)

        return result


    def hanzi2pinyin_split(self, string="", split="", firstcode=False):
        """提取中文的拼音
        @param string:要提取的中文
        @param split:分隔符
        @param firstcode: 提取的是全拼还是首字母？如果为true表示提取首字母，默认为False提取全拼
        """
        result = self.hanzi2pinyin(string=string, firstcode=firstcode)
        return split.join(result)
