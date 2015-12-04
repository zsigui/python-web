#!/usr/bin/env python
# encoding: utf-8

class ErrCode:

    # 成功
    SUCCESS = 0

    # 输入内容长度不符合，长度不足或超出
    ERR_LENGTH = 1

    # 输入内容类型不符合，如需要数字和字母一起
    ERR_TYPE = 2

    # 目录不存在，如创建失败或者没有此目录
    ERR_DIR = 3

    # 数据库出错，如获取或者插入失败
    ERR_DB = 4

    # 错误请求类型
    ERR_REQ = 5

    # 脚本异常错误
    ERR_EXEC = 6

    # 传入内容为空
    ERR_NONE = 9
