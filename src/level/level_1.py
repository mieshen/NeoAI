from level.common import generate_prompt

from level.operation_levels import operation_levels

def get_prompt(system_info):
    allowed_operations = """
  1. 运行大多数合法的 Python 代码。
  2. 使用系统命令（限制极危险操作）。
  3. 文件操作（创建、读取、删除文件）。
"""
    restrictions = """
  - 禁止执行以下极危险命令：
    1. 删除根目录（如 rm -rf /）。
    2. 删除系统关键文件夹（如 C:\\Windows）。
    3. 修改引导分区或删除分区表。
"""
    examples = """
⚠️ 示例（删除普通文件）：
>>>RUN>>>
import os
os.remove('example.txt')
<<<RUN<<<
"""
    return generate_prompt(1,system_info, allowed_operations, restrictions, examples, operation_levels)

