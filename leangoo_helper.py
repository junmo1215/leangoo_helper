# -*- coding: UTF-8 -*-
"""
主程序
"""
import leangoo_interface
import sys
VERSION = "v1.0"

class Enum(set):
    """生成枚举类型"""
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

def _show(key):
    """
    显示相应信息
    """
    if key == "welcome":
        # 进入程序时的引导
        print """
Welcome to leangoo_helper %s !
This is a tool to enhance leangoo. leangoo is a free, compact, light and visualized collaboration tools for agile development team

Type "help" for more information.""" % VERSION
    elif key == "help":
        # 帮助信息
        print """
This is the help utility.

Usage:
    <command> [options]
    
Commands:%s

General Options:%s""" % (_get_explanation("commands"), _get_explanation("general_options"))
    else:
        # 没有匹配项则抛出异常
        raise ValueError(key)

def _get_explanation(key):
    """获取指令和通用选项的说明列表"""
    if key == "commands":
        explanation_dict = COMMAND_AND_EXPLANATION
    elif key == "general_options":
        explanation_dict = GENERAL_OPTION_AND_EXPLANATION
    else:
        raise ValueError(key)

    if explanation_dict is None or explanation_dict == {}:
        return "\n\tThere is no %s" % key

    message = ""
    for command, explanation in explanation_dict.items():
        message += "\n\t %s \t\t %s" % (command, explanation)
    return message

def _process_function(cmd_input):
    inputs = cmd_input.split()
    function_name = inputs[0]
    arguments = inputs[1::]

    options = []
    # 分离通用选项和方法的参数
    for option in GENERAL_OPTION_AND_EXPLANATION.keys():
        if option in arguments:
            options.append(option)
            arguments.remove(option)

    if len(options) > 0:
        # 处理完通用选项之后就不执行这个方法了
        # 比如login -h email pwd这个命令的效果就只是看login这个命令的帮助
        _process_options(function_name, options)
        return

    # 调用对应的方法
    try:
        getattr(leangoo_interface, function_name)(*arguments)
    except AttributeError:
        raise AttributeError("ERROR: cmd '%s' is not found" % function_name)
    except TypeError:
        raise TypeError("ERROR: number of arguments is not match.")

def _process_options(function_name, options):
    if "-h" in options:
        # show help of this function
        _show_help_of_function(function_name)

def _show_help_of_function(function_name):
    """显示方法的帮助说明"""
    print """
Description: %s

Arguments: %s""" % (
    _get_function_description(function_name),
    _get_function_explanation(function_name))

def _get_function_description(function_name):
    """通过方法名获取方法的描述"""
    return "\n\t %s" % FUNCTION_AND_EXPLANATION[function_name]["Description"]

def _get_function_explanation(function_name):
    """通过方法名获取方法参数以及说明"""
    options = FUNCTION_AND_EXPLANATION[function_name]["Options"]
    if options == {}:
        return "\n\t %s" % "This function need no arguments."
    message = ""
    for command, explanation in options.items():
        message += "\n\t %s \t\t %s" % (command, explanation)
    return message

def _process_cmd(cmd_input):
    """处理用户输入的指令"""
    # 退出指令单独处理，因为返回值和其他的不同
    if cmd_input in SYSTEM_CMD["end_keys"]:
        return STATUSENUM.END

    if _is_system_cmd(cmd_input):
        _process_system_cmd(cmd_input)
    else:
        _process_function(cmd_input)

    return STATUSENUM.WAIT_CMD

def _process_system_cmd(cmd_input):
    """处理除退出指令之外的系统指令"""
    if cmd_input in SYSTEM_CMD["help_keys"]:
        _show("help")

def _is_system_cmd(cmd_input):
    """判断当前指令是否是系统指令"""
    for key_collection in SYSTEM_CMD.values():
        if cmd_input in key_collection:
            return True
    return False

def _exit_leangoo_helper():
    """退出当前程序"""
    pass

# 当前状态
STATUSENUM = Enum(["BEGIN", "END", "WAIT_CMD", "PROCESS_CMD"])
STATUS = STATUSENUM.BEGIN
PROMPT = "\n>>> "

# 系统指令
SYSTEM_CMD = {
    "help_keys" : ["help"],
    "end_keys" : ["exit"]
}

# 命令以及说明
COMMAND_AND_EXPLANATION = {
    "help": "Show help for commands.",
    "exit": "exit leangoo_helper."
}

# 通用选项及说明
GENERAL_OPTION_AND_EXPLANATION = {
    "-h": "Show help."
}

# 关于每个方法的介绍以及参数说明
# 在interface中新增的方法都要在这里添加说明
FUNCTION_AND_EXPLANATION = {
    "items_to_tasks": {
        "Description": "Read items from a task and add them to a list.",
        "Options": {
            "task": "A name or id for the task\
(if there are some task with same name, return the first one).",
            "position_x": "Zero-based index of list in x-axis.",
            "position_y": "Zero-based index of lane in y-axis."
        }
    },
    "login":{
        "Description": "Login leangoo with email and password.",
        "Options":{
            "email": "Your email for login leangoo.",
            "pwd": "Your password in leangoo."
        }
    },
    "open_board_by_id": {
        "Description": "Open a board so that you can operate in the board, \
if you had and change in the browser, \
you need to use open_board_by_id to refresh data.",
        "Options": {
            "board_id": "id of the board(you can get it at the last of url)."
        }
    }
}

def main():
    """
    主程序
    """
    global STATUS
    _show("welcome")
    STATUS = STATUSENUM.WAIT_CMD

    while STATUS <> STATUSENUM.END:
        # cmd_input = raw_input(PROMPT)
        # STATUS = _process_cmd(cmd_input.strip())
        try:
            cmd_input = raw_input(PROMPT).decode(sys.stdin.encoding)
            STATUS = _process_cmd(cmd_input.strip())
        except Exception as e:
            STATUS = STATUSENUM.WAIT_CMD
            print e

    _exit_leangoo_helper()

if __name__ == '__main__':
    main()
