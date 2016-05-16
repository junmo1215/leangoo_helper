# -*- coding: UTF-8 -*-
"""
主程序
"""
import leangoo_interface
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
    """获取说明列表"""
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

    #print "interface_name is %s and arguments are %s" % (function_name, arguments)
    options = []
    for option in GENERAL_OPTION_AND_EXPLANATION.keys():
        if option in arguments:
            options += option
            arguments.remove(option)

    _process_options(function_name, options)

    # if GENERAL_OPTION_AND_EXPLANATION.keys() in arguments:
    #     _process_options(function_name, arguments)
    #     return

    # 调用对应的方法
    try:
        getattr(leangoo_interface, function_name)(*arguments)
    except AttributeError:
        print "ERROR: cmd '%s' is not found" % function_name
    except TypeError:
        print "ERROR: number of arguments is not match."

def _process_options(function_name, options):
    if options == "-h":
        # show help of this function
        pass


def _process_cmd(cmd_input):
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
FUNCTION_AND_EXPLANATION = {
    "items_to_tasks": {
        "Description": "Read items from a task and add them to a list.",
        "Options": {
            "": ""
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
        try:
            cmd_input = raw_input(PROMPT)
            STATUS = _process_cmd(cmd_input.strip())
        except Exception as e:
            STATUS = STATUSENUM.WAIT_CMD
            print e

    _exit_leangoo_helper()

if __name__ == '__main__':
    main()
