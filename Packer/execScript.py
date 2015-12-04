#!/usr/bin/env python
# encoding: utf-8

import sys
sys.path.append(".")
from file.script.config import ConfigParse
from file.script.core import main
import md_util
import os
from convert_pinyin import PinYin


def execScript(game, channels, modifyTestMode=False, sedCommand=None):
    reload(sys)
    sys.setdefaultencoding('utf8')
    ConfigParse.shareInstance().readUserConfig()
    for chn in channels:
        print '================================================'
        print 'channel name : ' + chn['name']
        print '================================================'
        main(game, chn, modifyTestMode, sedCommand)

