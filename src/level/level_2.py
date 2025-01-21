import importlib
import os
import configparser


def get_prompt(system_info):
    """
    根据安全等级动态生成 Prompt 的参数并传递给 generate_prompt。
    """
    level = 2
    # 从 main 模块获取 config
    main_module = importlib.import_module("main")
    config = getattr(main_module, "config")

    # 使用 config 中的 LANGUAGE
    language_code = config["LANGUAGE"]

    # 构造语言文件路径（动态根据语言代码）
    main_dir = os.path.dirname(os.path.abspath(main_module.__file__))  # 获取主运行目录
    locale_dir = os.path.join(
        main_dir, "locale", "prompt", language_code
    )  # 动态语言目录
    levels_file_path = os.path.join(
        locale_dir, "levels.ini"
    )  # 动态加载 levels.ini 文件

    # 检查文件是否存在
    if not os.path.exists(levels_file_path):
        raise FileNotFoundError(f"语言文件 '{levels_file_path}' 不存在！")

    # 加载等级配置
    allowed_operations, restrictions, examples = load_level_configuration(
        levels_file_path, level
    )

    # 调用 generate_prompt
    from level.common import generate_prompt
    from level.operation_levels import operation_levels

    return generate_prompt(
        level, system_info, allowed_operations, restrictions, examples, operation_levels
    )


def load_level_configuration(file_path, level):
    """
    从 ini 文件加载指定安全等级的配置内容。
    """
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read(file_path, encoding="utf-8")

    # 构造等级 section
    section = f"level_{level}"
    if section not in parser:
        raise ValueError(f"配置文件中未找到 '{section}' 配置项！")

    # 获取配置项
    allowed_operations = parser.get(section, "allowed_operations", fallback="").strip()
    restrictions = parser.get(section, "restrictions", fallback="").strip()
    examples = parser.get(section, "examples", fallback="").strip()

    return allowed_operations, restrictions, examples
