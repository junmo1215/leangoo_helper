# -*- coding: UTF-8 -*-

# from leangoo_core import *

class l_task(object):
    def __init__(self, task_id, task_name, board_id, list_id, block_id, chklst=[]):
        self.task_id = task_id
        self.task_name = task_name
        self.board_id = board_id        
        self.list_id = list_id
        self.block_id = block_id
        self.chklst = chklst

class l_list(object):
    def __init__(self, list_id, list_name, board_id, current_index=999999):
        self.list_id = list_id
        self.list_name = list_name

    def __str__(self):
        return "list_id: %s    list_name: %s" % (self.list_id, self.list_name)

class l_board(object):
    def __init__(self, board_id, board_name=""):
        self.board_id = board_id
        self.board_name = board_name
        self.token = ""
        self.lists = []
        self.tasks = {}
        self.blocks = []

    def get_task(self, task_id):
        return self.tasks[task_id]

class l_chklst(object):
    def __init__(self, item_id, item_name, status):
        self.item_id = item_id
        self.item_name = item_name
        self.status = status

class l_block(object):
    def __init__(self, block_id, list_id, lane_id):
        self.block_id = block_id
        self.list_id = list_id
        self.lane_id = lane_id

class LoginError(RuntimeError):
    """登录失败的异常"""
    pass
