import importlib
import os
import re


def generate_prompt(level, system_info, allowed_operations, restrictions, examples, operation_levels):
    """
    动态生成 Prompt，并让 AI 自行判断权限是否足够。
    """
    main_module = importlib.import_module("main")
    config = getattr(main_module, "config")

    # 使用 config 中的 LANGUAGE
    language_code = config["LANGUAGE"]
    # 构造语言文件路径
    main_dir = os.path.dirname(os.path.abspath(main_module.__file__))

    
    locale_dir = os.path.join(main_dir, "locale", "prompt", language_code)
    file_path = os.path.join(locale_dir, f"{language_code}.txt")
    
    # 确保文件存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Language template file '{file_path}' not found.")
    
    # 读取模板文件内容
    with open(file_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()
    
    # 准备替换的内容
    system_info_text = "\n".join([f"{key}: {value}" for key, value in system_info.items()])
    operation_levels_text = "\n".join([f"{key}: Level {value}" for key, value in operation_levels.items()])

    # 使用格式化方法填充模板
    prompt = prompt_template.format(
        level=level,
        system_info_text=system_info_text,
        operation_levels_text=operation_levels_text,
        allowed_operations=allowed_operations,
        restrictions=restrictions,
        examples=examples,
    )
    
    return prompt


def extract_code(ai_response):
    """
    提取 AI 响应中的代码块。
    """
    import re
    match = re.search(r">>>RUN>>>[\s\S]*?<<<RUN<<<", ai_response)
    if match:
        return match.group(0).replace(">>>RUN>>>", "").replace("<<<RUN<<<", "").strip()
    return None
