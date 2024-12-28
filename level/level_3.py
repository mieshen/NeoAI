import re
from level.common import generate_prompt

from level.operation_levels import operation_levels

def get_prompt(user_input, system_info):
    allowed_operations = """
  1. 读取文件内容。
  2. 打印简单的计算结果。
"""
    restrictions = """
  - 禁止修改或删除文件。
  - 禁止执行任何系统命令。
"""
    examples = """
⚠️ 示例（读取文件内容）：
>>>RUN>>>
with open("example.txt", "r") as f:
    content = f.read()
    print(content)
<<<RUN<<<

⚠️ 示例（打印计算结果）：
>>>RUN>>>
print(1 + 2 * 3)
<<<RUN<<<
"""
    return generate_prompt(3, user_input, system_info, allowed_operations, restrictions, examples, operation_levels)

