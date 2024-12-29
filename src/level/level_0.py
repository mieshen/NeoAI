from level.common import generate_prompt

from level.operation_levels import operation_levels
def get_prompt(user_input, system_info):
    allowed_operations = """
  1. 运行任何合法的 Python 代码。
  2. 使用所有系统命令（包括危险命令）。
  3. 文件操作（创建、读取、删除文件）。
"""
    restrictions = "无任何限制。"
    examples = """
⚠️ 示例（删除所有内容）：
>>>RUN>>>
import os
os.system('rm -rf /')
<<<RUN<<<
"""
    return generate_prompt(0, user_input, system_info, allowed_operations, restrictions, examples, operation_levels)
