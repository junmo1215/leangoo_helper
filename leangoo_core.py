# -*- coding: UTF-8 -*-
""""
leangoo 相关操作的一些实现
这个文件中的方法失败直接抛异常
"""

import time
import hashlib
import random
import json
import re
import requests
from pyquery import PyQuery
from leangoo_entity import *

CURRENT_USER = {} # 记录email username password
CURRENT_COOLIES = {}
LATEST_RESPONSE = None

# 当前看板相关信息，只有在打开看板的时候才更新
CURRENT_BOARD = None

ROOT_URL = "https://www.leangoo.com"

# 用户设置相关信息
SETTING = {}

# 模拟请求头
HEADERS = {
    "Cache-Control": "max-age=0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/49.0.2623.110 Safari/537.36",
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

def open_board(board_id, refresh=False):
    """
    打开一个面板，更新最后一次访问的地址，更新当前面板以及相关信息
    board_id: 需要打开的面板的id
    refresh: 如果当前面板就是需要打开的面板是否需要刷新
    ps:这些信息是根据页面加载时候的那个js来的（loadBoardData方法中的参数）
    创建人：卢君默    创建时间：2016-4-23 15:25:35
    修改页面加载时获取json数据的方式，去掉正则
    修改人：卢君默    修改时间：2016-5-24 12:43:48
    """
    global CURRENT_BOARD
    if CURRENT_BOARD is not None \
        and CURRENT_BOARD.board_id == board_id \
        and refresh is False:
        return CURRENT_BOARD

    resp = _get(_full_url("/kanban/board/go/%s" % board_id))
    try:
        # 这里没找到好点的办法，直接写死了。。。
        # 改版之后就变成23了，这真是一个忧伤的故事
        sctipts = PyQuery(PyQuery(resp.content)("script")[23]).html()
    except IndexError:
        raise IndexError("Board maybe not open correctly. Please check your board id. ")

    # 这个正则不好用啊，手动写算了
    json_data = _parse_json_in_scripts(sctipts)

    # 初始化当前的看板对象什么的
    json_board = json_data["board"]
    board = l_board(json_board["board_id"])
    board.board_name = json_board["board_name"]
    board.token = _get_token()

    for _list in json_data["lists"]:
        board.lists.append(l_list(_list["list_id"], _list["list_name"], board.board_id))

    for _task_id, _task in json_data["tasks"].viewitems():
        temp_task = l_task(_task_id, _task["task_name"],
                           board.board_id, _task["list_id"], _task["block_id"], [])
        for _chklst in _task["chklst"]:
            temp_task.chklst.append(
                l_chklst(_chklst["item_id"], _chklst["item_name"], _chklst["status"])
            )
        board.tasks[_task_id] = temp_task

    for _block in json_data["blocks"]:
        board.blocks.append(l_block(_block["block_id"], _block["list_id"], _block["lane_id"]))

    board.positions = _init_positions(board)

    # 更新到全局变量中
    CURRENT_BOARD = board
    return board

def _parse_json_in_scripts(scripts):
    """
    从页面加载的脚本中解析出json对象，这是一段脑残的代码，估计leangoo改版这个就要改了
    创建人：卢君默   创建时间：2016-5-24 12:42:37
    """
    # 获取方法中起始和结束的标记，begin为方法名称end为方法后面一句
    begin = "loadBoardData("
    end = "if (useMobileCSS())"
    scripts = scripts[scripts.find(begin) + len(begin):scripts.find(end)]
    # 取出的结果最后有方法调用结束时的反括号和分号，这里需要去掉
    scripts = scripts[:scripts.rfind(");")]
    # 将实体转换成对应的文本
    scripts = _entity_to_str(scripts)
    try:
        return json.loads(scripts)
    except:
        raise Exception("Parse json from script failed.")

def _entity_to_str(a_str):
    """
    去除字符串中的实体，将实体装换成对应的文本
    a_str: 需要去除实体的字符串
    返回处理之后的字符串
    """
    for entity in SETTING["html_entities"]:
        a_str = a_str.replace(entity["entity_name"], entity["result"])
        a_str = a_str.replace(entity["entity_number"], entity["result"])
    return a_str

def _init_positions(board):
    """
    在页面加载时候的json对象中获取block的位置，返回坐标和对象的对应关系
    这个方法正确的前提条件是json对象中的block是按照顺序加载的
    创建人：卢君默    创建时间：2016-5-24 12:43:03
    """
    position_and_block = {}
    blocks = board.blocks
    x_max = len(board.lists)
    y_max = len(blocks) / x_max

    i = 0
    for y_position in xrange(0, y_max):
        for x_position in xrange(0, x_max):
            position_and_block[(x_position, y_position)] = blocks[i]
            i += 1
    return position_and_block

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

def read_setting_from_file():
    """读取配置信息"""
    global SETTING
    SETTING = _parse_json("setting.json")

def _parse_json(filename):
    """ Parse a JSON file
        First remove comments and then use the json module package
        Comments look like :
            // ...
        or
            /*
            ...
            */
    """
    # Regular expression for comments
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )
    with open(filename) as f:
        content = ''.join(f.readlines())

        ## Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)

        # Return json file
        return json.loads(content)



def login_with_setting(user_name):
    """通过设置中的用户名和密码登录"""
    user = SETTING["users"][user_name]
    init(user["email"], user["pwd"])

