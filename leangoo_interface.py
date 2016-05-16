# -*- coding: UTF-8 -*-
"""
为主程序提供调用接口
"""

import requests
from pyquery import PyQuery
from leangoo_core import *
from leangoo_entity import *
import msvcrt, sys

import time
import threading

def _getpass(prompt='Password:'):
    """
    获取用户输入的密码，在控制台输入的时候显示星号
    """
    count = 0
    chars = []
    for xchar in prompt:
        msvcrt.putch(xchar)
    while True:
        new_char = msvcrt.getch()
        if new_char in '\r\n':
            break
        elif new_char == '\0x3': #ctrl + c
            raise KeyboardInterrupt
        elif new_char == '\b':
            if chars and count >= 0:
                count -= 1
                chars = chars[:-1]
                msvcrt.putch('\b')
                msvcrt.putch('\x20')#space
                msvcrt.putch('\b')
        else:
            if count < 0:
                count = 0
            count += 1
            chars.append(new_char)
            msvcrt.putch('*')
    return ''.join(chars)

def login(email, pwd):
    """登录"""
    print u"%s调用成功啦，参数为%s %s" % ("login", email, pwd)
    # while is_init() is False:
    #     # print u"请输入登录邮箱和密码！"
    #     print "please input your email and password"
    #     email = raw_input(u">>> email:")
    #     # pwd = raw_input(u"密码:")
    #     pwd = _getpass(">>> password:")
    #     try:
    #         init(email, pwd)
    #     except Exception as e:
    #         print e.message
    #     print ""

def items_to_task():
    print ""    