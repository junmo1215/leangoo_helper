# -*- coding: UTF-8 -*-
from nose.tools import *
from leangoo_helper.leangoo_core import *

assert is_init() == False

def test_init():
    email = "lujunmo1992@126.com"
    p = "leangoolean92"
    try:
        init(email, p)
    except LoginError as e:
        pass
    else:
        assert get_username() == "lean92"
        assert get_email() == "lujunmo1992@126.com"

email = "lujunmo1992@126.com"
p = "leangoolean92"
username = "lean92"
init(email, p)

def test_is_init():
    assert is_init() == True

def test_get_cookies():
    cookies = get_cookies()
    assert len(cookies) >= 3
    assert cookies.has_key("info1")
    assert cookies.has_key("info2")
    assert cookies.has_key("PHPSESSID")

def test_new_id():
    open_board("1081970")
    for i in xrange(0, 10):
        sid = new_id()
        assert len(sid) == 16
        assert ("g" in sid) == False

def test_get_username():
    assert get_username() == username

def test_get_email():
    assert get_email() == email

def test_chklst_add_item():
    board_id = "1081970"
    task_id = "2dc33d8c35a05361"
    task_name = u"asdasdadasdasdasdasd"
    test_task = open_board(board_id).tasks[task_id]
    assert test_task.task_id == task_id
    assert test_task.task_name == task_name
    length_before = len(test_task.chklst)
    chklst_add_item(task_id, "2、中文", board_id)
    test_task = get_current_board().tasks[task_id]
    assert test_task.task_id == task_id
    assert test_task.task_name == task_name
    length_after = len(test_task.chklst)
    assert length_after == length_before + 1
    # id重复时会抛异常
    try:
        chklst_add_item(task_id, "2、中文", board_id, "343e259f10132b91")
    except Exception as e:
        assert e.message <> ""
    assert test_task == get_current_board().tasks[task_id]

def test_chklst_get_items():
    board_id = "1081970"
    task_id = "350d4a03d5f13c5f"
    new_check_item_name = "test_chklst_get_items"
    chklst_before = chklst_get_items(task_id, board_id)
    chklst_add_item(task_id, "test_chklst_get_items", board_id)
    chklst_after = chklst_get_items(task_id, board_id)
    assert len(chklst_before) + 1 == len(chklst_after)
    chklst_before.append(new_check_item_name)
    assert chklst_after == chklst_before

def test_add_task():
    board_id = "1081970"
    # 这三个一旦确定了blocks就能确定下来了
    block_id = "203de10b18dbdcb3"
    list_id = "740152"
    lane_id = "0000000001081970"

    new_task_name = "我就试试新增一个任务"

    board = open_board(board_id)
    # 这里要注意不新建dict的话是引用类型，修改current_board的同时会修改tasks_before
    # 这个问题坑了20多分钟，，，一直以为是代码有问题。。。
    tasks_before = dict(board.tasks)
    add_task(new_task_name, board_id, lane_id, list_id, block_id)
    tasks_after = get_current_board().tasks
    assert len(tasks_before) + 1 == len(tasks_after)

def test_get_task():
    ids = get_tasks(u"asdasdadasdasdasdasd", "1081970")
    assert len(ids) == 1
    assert ids[0].task_id == "2dc33d8c35a05361"




