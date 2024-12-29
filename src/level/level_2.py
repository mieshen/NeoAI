from level.common import generate_prompt

from level.operation_levels import operation_levels
def get_prompt(user_input, system_info):
    allowed_operations = """
  1. 文件操作（创建、读取、删除文件）。
  2. 执行部分系统命令（如打开任务管理器或资源管理器）。
"""
    restrictions = """
  - 禁止执行高风险命令（如删除系统文件夹、修改系统配置）。
  - 禁止运行未知的外部程序。
"""
    examples = """
⚠️ 示例（打开任务管理器）：
>>>RUN>>>
import os
os.system('taskmgr')
<<<RUN<<<

⚠️ 示例（删除文件）：
>>>RUN>>>
import os
os.remove('example.txt')
<<<RUN<<<
"""
    return generate_prompt(2, user_input, system_info, allowed_operations, restrictions, examples, operation_levels)

