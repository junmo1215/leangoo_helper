# -*- coding: UTF-8 -*-
"""
为主程序提供调用接口
在这个文件中增加的方法都需要在leangoo_helper中说明
维护 FUNCTION_AND_EXPLANATION
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
    # 在输入之后回车，防止下一个输出直接接在在密码后面
    print ""
    return ''.join(chars)

def check_login(func):
    """用来检查用户是否登录的装饰器"""
    def wrapper(*args, **kw):
        """抽象装饰器中的方法"""
        if is_init() is False:
            print "You need login first."
            login()
            if is_init() is False:
                # 这里抛异常防止继续执行后面的代码
                raise LoginError("")
        return func(*args, **kw)
    return wrapper

def login(email="", pwd=""):
    """登录"""
    # print u"%s调用成功啦，参数为%s %s" % ("login", email, pwd)
    if email == "":
        email = raw_input("Please input your email: ")
    if pwd == "":
        pwd = _getpass("Password: ")
    try:
        init(email, pwd)
    except LoginError as error:
        print error

@check_login
def items_to_tasks():
    """将工作项转换为任务"""
    print "items_to_task"
