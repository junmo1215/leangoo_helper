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

def check_open_board(func):
    """用来检查用户是否打开了一个看板的装饰器"""
    def wrapper(*args, **kw):
        """对下面的方法进行封装"""
        if get_current_board() is None:
            print "You need open a board."
            board_id = raw_input("Please input a id to open the board: ")
            open_board(board_id)
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
        print error.message

@check_login
@check_open_board
def items_to_tasks(task, position_x=0, position_y=0):
    """
    将检查项项转换为任务
    task: 工作项（id或名称，如果名称有重复的则定位为第一个）
    position：需要放置检查项的block的位置，按行列给出坐标（索引初始值为0，原点在左上角）
    """
    task_id = ""
    current_board = get_current_board()
    for _id, _task in current_board.tasks.items():
        # 根据id和name找到task_id，只要有一个匹配上了就行
        if task in [_task.task_id, _task.task_name]:
            task_id = _id
            break
    if task_id == "":
        raise Exception('ERROR: task "%s" not found' % task)

    position = (int(position_x), int(position_y))
    if current_board.positions.has_key(position) is False:
        raise Exception('ERROR: position "%s" out of range' % position)

    block = current_board.positions[position]
    # 获取检查项
    chklst = chklst_get_items(task_id, current_board.board_id)

    for i in xrange(0, len(chklst)):
        add_task_thread = \
            threading.Thread(target=add_task,
                             args=(chklst[i], current_board.board_id,
                                   block.lane_id, block.list_id, block.block_id, ),
                             name="add_task_%s" % i)
        add_task_thread.start()
    add_task_thread.join()

@check_login
def open_board_by_id(board_id):
    """通过id打开看板，如果看板已打开则刷新数据"""
    open_board(board_id, True)
