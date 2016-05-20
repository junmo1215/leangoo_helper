# -*- coding: UTF-8 -*-
""""
leangoo 相关操作的一些实现
这个文件中的方法失败直接抛异常
"""

import requests
from pyquery import PyQuery
import time
import hashlib   
import random
import json
from leangoo_entity import *
import re

CURRENT_USER = {} # 记录email username password
CURRENT_COOLIES = {}
LATEST_RESPONSE = None

# 当前看板相关信息，只有在打开看板的时候才更新
CURRENT_BOARD = None

ROOT_URL = "https://www.leangoo.com"
# 模拟请求头
HEADERS = {
    "Cache-Control": "max-age=0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Upgrade-Insecure-Requests": "1"
}

def is_init():
    """
    判断是否初始化，使用之前应当用用户名和密码初始化一下
    创建人：卢君默    创建时间：2016-4-22 13:58:38
    """
    return CURRENT_USER.has_key("username") and CURRENT_USER.get("username") <> ""

def init(email, password):
    """
    执行初始化
    username:用户名
    password：密码
    创建人：卢君默
    创建时间：2016-4-21 13:41:55
    """
    global CURRENT_COOLIES
    #好像登录前注销没有什么意义，暂时先不处理
    #logout()
    login_url = _full_url("/kanban/login/go")
    # 构造登录时需要的数据
    data = {
        "from_page": "",
        "email": email,
        "pwd": password,
        "loginRemPwdVal": "true"
    }
    CURRENT_COOLIES = {
        "PHPSESSID": "shuc48lfj13g8q8f805obem1u1"
    }
    resp = _post(login_url, data=data)

    # leangoo首页登录返回方式改掉了，现在是返回json字符串
    response_data = json.loads(resp.text)
    if response_data["succeed"] is False:
        raise LoginError(response_data["message"])

    # 应该是用户认证信息相关的cookie，每次请求好像都会把这个发过去
    for cookie in resp.cookies:
        CURRENT_COOLIES[cookie.name] = cookie.value

    # 更新当前登录人信息
    CURRENT_USER["email"] = email
    CURRENT_USER["password"] = password
    # 在看板列表界面才取的到用户名，之前又一次跳转所以不需要在代码里面请求这个地址
    # 改版之后跳转写在了js里面，所以这里需要手动请求一次
    resp = _get(response_data["message"])
    CURRENT_USER["username"] = _get_username_after_login(resp)

def logout():
    """
    注销登录
    创建人：卢君默    创建时间：2016-4-22 13:58:56
    """
    logout_url = _full_url("/kanban/login/logout")
    _get(logout_url)

def _get_username_after_login(resp):
    """
    在输入密码后跳转的页面中获取用户名
    创建人：卢君默    创建时间：2016-4-22 13:59:06
    """
    return PyQuery(PyQuery(resp.text)("#nav_user_name")).text()

def _full_url(url):
    """
    根据相对路径获取完整的url
    创建人：卢君默    创建时间：2016-4-22 13:59:15
    """
    return ROOT_URL + url

def get_cookies():
    """
    返回现在的cookie
    创建人：卢君默    创建时间：2016-4-22 13:59:23
    """
    return CURRENT_COOLIES

def check_str_is_empty(*strs):
    """
    检查参数中的字符串是否为空，为空则抛出异常
    创建人：卢君默    创建时间：2016-4-22 14:10:45
    """
    for _str in strs:
        if _str == "":
            raise Exception("存在空字符串")

def _get(url, data=None, is_update_response=True):
    """
    封装get方法
    url：绝对地址
    data：带的参数
    is_update_response: 是否更新最后一次相应信息
    创建人：卢君默    创建时间：2016-4-22 16:06:47
    """
    global LATEST_RESPONSE
    resp = requests.get(url, headers=HEADERS, data=data, cookies=CURRENT_COOLIES, verify=False)
    if is_update_response:
        LATEST_RESPONSE = resp
    return resp

def _post(url, data=None, is_update_response=True):
    """
    封装post方法
    url：绝对地址
    data：带的参数
    is_update_response: 是否更新最后一次相应信息
    创建人：卢君默    创建时间：2016-4-22 16:07:34
    """
    global LATEST_RESPONSE
    resp = requests.post(url, headers=HEADERS, data=data, cookies=CURRENT_COOLIES, verify=False)
    if is_update_response:
        LATEST_RESPONSE = resp
    return resp

def new_id():
    """
    生成leangoo里面用的这种奇怪的id
    ps:js代码
    function createId() {
        var a = (new Date).getTime(),
        c = (Math.random().toString(16) + "000000000").substr(2, 8);
        return $.md5(token + a + c)
    }
    创建人：卢君默    创建时间：2016-4-22 18:38:25
    """
    a = str(time.time() * 1000)
    c = str(hex(int(random.random() * 100000000)))[2:8]
    s_md5 = hashlib.md5()
    s_md5.update(_get_token() + a + c)
    return s_md5.hexdigest()[8:-8]

def _get_token():
    """
    获取页面中的token值
    创建人：卢君默    创建时间：2016-4-22 18:38:13
    """
    # 如果能从board中取到值则直接返回
    if CURRENT_BOARD is not None and CURRENT_BOARD.token <> "":
        return CURRENT_BOARD.token

    val = PyQuery(LATEST_RESPONSE.text)("#token").val()
    if val is None:
        raise Exception("未能从当前页面中获取token值")
    return val

def _has_token():
    """
    判断能否获取到token
    创建人：卢君默    创建时间：2016-4-23 15:52:56
    """
    return ((CURRENT_BOARD <> None and CURRENT_BOARD.token <> "")
            or PyQuery(LATEST_RESPONSE.text)("#token").val() is not None)

def get_username():
    """
    获取当前操作人的用户名
    创建人：卢君默    创建时间：2016-4-22 14:02:51
    """
    if is_init() is False:
        raise LoginError("Need login")
    return CURRENT_USER["username"]

def get_email():
    """
    获取当前操作人的用户名
    创建人：卢君默    创建时间：2016-4-22 14:38:24
    """
    if is_init() is False:
        raise LoginError("Need login")
    return CURRENT_USER["email"]

def chklst_add_item(task_id, item_name, board_id, item_id=""):
    """
    添加检查项
    task_id:任务id
    item_name:检查项内容
    board_id:看板id
    item_id:检查项id(没有就新增一个)
    创建人：卢君默    创建时间：2016-4-23 12:31:37
    """
    global CURRENT_BOARD
    if item_id == "":
        item_id = _try_get_new_id(board_id)

    data = {
        "task_id": task_id,
        "item_name": item_name,
        "item_id": item_id,
        "board_id": board_id
        }
    resp = _post(_full_url("/kanban/chklst/addItem"), data)

    # 检查请求是否有异常
    _check_response(resp)

    # 更新全局变量
    if _is_current_board(board_id):
        # status默认值为1
        (CURRENT_BOARD.tasks)[task_id].chklst.append(l_chklst(item_id, item_name, "1"))

def _try_get_new_id(board_id):
    """
    在相应面板内新建id
    创建人：卢君默    创建时间：2016-4-23 17:13:10
    """
    # 如果获取不到token，创建id之前访问任务所在的页面，需要取这个页面的token
    if _has_token() is False:
        _get(_full_url("/kanban/board/go/%s" % board_id))
    return new_id()

def _is_current_board(board_id):
    """
    是否为当前打开的面板
    创建人：卢君默    创建时间：2016-4-23 16:29:49
    """
    return board_id == CURRENT_BOARD.board_id

def open_board(board_id):
    """
    打开一个面板，更新最后一次访问的地址，更新当前面板以及相关信息
    ps:这些信息是根据页面加载时候的那个js来的（loadBoardData方法中的参数）
    创建人：卢君默    创建时间：2016-4-23 15:25:35
    """
    global CURRENT_BOARD
    if CURRENT_BOARD is not None and CURRENT_BOARD.board_id == board_id:
        return CURRENT_BOARD

    resp = _get(_full_url("/kanban/board/go/%s" % board_id))
    # 这里没找到好点的办法，直接写死了。。。
    sctipts = PyQuery(PyQuery(resp.content)("script")[22]).html()

    # 解析html，得到页面加载时候的看板信息
    match_result = re.findall(ur"(?<=loadBoardData[\(])[^\)）]+(?=[\)])", sctipts)
    if len(match_result) == 0:
        raise Exception("解析页面信息出错，未能获取此看板中的相关信息")
    json_data = json.loads(match_result[0])

    # 初始化当前的看板对象什么的
    json_board = json_data["board"]
    board = l_board(json_board["board_id"])
    board.board_name = json_board["board_name"]
    board.token = _get_token()

    for _list in json_data["lists"]:
        board.lists.append(l_list(_list["list_id"], _list["list_name"], board.board_id))

    for _task_id, _task in json_data["tasks"].viewitems():
        temp_task = l_task(_task_id, _task["task_name"],
                           board.board_id, _task["list_id"], _task["block_id"])
        for _chklst in _task["chklst"]:
            temp_task.chklst.append(
                l_chklst(_chklst["item_id"], _chklst["item_name"], _chklst["status"])
            )
        board.tasks[_task_id] = temp_task

    for _block in json_data["blocks"]:
        board.blocks.append(l_block(_block["block_id"], _block["list_id"], _block["lane_id"]))

    # 更新到全局变量中
    CURRENT_BOARD = board
    return board

def get_current_board():
    """
    获取当前看板信息
    创建人：卢君默    创建时间：2016-4-23 15:41:41
    """
    return CURRENT_BOARD

def chklst_get_items(task_id, board_id):
    """
    获取检查项
    task_id:任务Id
    board_id:看板id
    创建人：卢君默    创建时间：2016-4-23 16:57:02
    """

    if _is_current_board(board_id) is False:
        # 不是获取的当前面板时需要打开对应的面板
        open_board(board_id)

    task = CURRENT_BOARD.get_task(task_id)
    result = []
    for chklst in task.chklst:
        result.append(chklst.item_name)
    return result

def get_tasks(task_name, board_id):
    """
    通过任务名称获取task列表（如果没有则返回None）
    按道理是返回一个的，但是task_name可能重复
    """
    board = open_board(board_id)
    result = []
    print board.tasks
    for _task in board.tasks.values():
        print _task
        if _task.task_name == task_name:
            result.append(_task)
    return result

def add_task(new_task_name, board_id, lane_id, list_id,
             block_id, task_id="", position_before_task=""):
    """
    添加任务
    """
    global CURRENT_BOARD
    if task_id == "":
        task_id = _try_get_new_id(board_id)
    resp = _post(_full_url("/kanban/task/add"), {
        "new_task_name": new_task_name,
        "board_id": board_id,
        "lane_id": lane_id,
        "list_id": list_id,
        "block_id": block_id,
        "task_id": task_id,
        "list_name": list_name(list_id, board_id),
        "position_before_task": position_before_task
    })
    # 检查请求是否有异常
    _check_response(resp)

    # 更新全局变量
    (CURRENT_BOARD.tasks)[task_id] = l_task(task_id, new_task_name, board_id, list_id, block_id)

def list_name(list_id, board_id=""):
    """
    根据list_id获取list_name
    创建人：卢君默    创建时间：2016-4-23 17:34:49
    """
    if board_id == "":
        board = CURRENT_BOARD
    else:
        board = open_board(board_id)

    for _list in board.lists:
        if _list.list_id == list_id:
            return _list.list_name
    raise Exception("List not found. list_id: %s" % list_id)

def _check_response(resp):
    """
    检查请求的返回值是否正常
    创建人：卢君默    创建时间：2016-4-23 17:20:42
    """
    if resp.status_code <> 200:
        raise Exception("网络请求失败")

    if resp.content <> "":
        result = json.loads(resp.content)
        if result["succeed"] is False:
            raise Exception(result["message"])

def edit_task(edit_task_name, task_id, board_id):
    """编辑任务"""
    pass

def get_tasks_in_list(list_id, board_id=""):
    """
    获取指定list中的task列表
    """
    check_str_is_empty(list_id)

    if board_id == "":
        board = CURRENT_BOARD
    else:
        board = open_board(board_id)

    result = []
    for _task in board.tasks.values():
        if _task.list_id == list_id:
            result.append(_task)

    return result


