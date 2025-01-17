import ast
import os
import re
import subprocess
import tempfile
import shutil
import json  # 用于持久化配置
from utils.output_handler import OutputHandler
from utils.scripts_handler import cleanup_temp_dir, execute_in_subprocess
from utils.system_info import get_system_info
from utils.ai_interaction import get_ai_response, replace_last_history
from level.operation_levels import operation_levels
from level.common import extract_callback, generate_prompt, extract_code
from utils.ai_interaction import append_to_last_history
from utils.help_handler import show_help


# === 配置常量 === #
CONFIG_FILE = os.path.join(os.getcwd(), "config.json")  # 配置文件路径
DEFAULT_CONFIG = {
    "API_KEY": "YOUR_API_KEY",
    "API_BASE_URL": "https://api.openai.com/v1/chat/completions",
    "MODEL": "gpt-4o",
    "EXECUTION_LEVEL": 2,
    "LOOP": True,
    "LOG_OUTPUT": False,
    "RETURN_TIMEOUT": -1,  # -1 为自适应超时，大于 0 为固定超时
    "TEMPERATURE": 0.7,
    "MAX_TOKENS": 4096,
    "MAX_TURNS": 32,
    "LANGUAGE": "en",
    "EXTRA_PROMPT": "NONE",
}
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
VERSION = "0.13.2-beta+20250207"
WEB_UI_URL = None


def save_config():
    """
    将当前配置保存到 config.json 文件中。

    此函数会尝试将全局配置变量 'config' 以 JSON 格式写入到指定的配置文件路径中。
    如果写入过程中出现任何异常，将在终端打印 "save failed"。
    """
    """
    将当前配置保存到 config.json 文件中。

    此函数会尝试将全局配置变量 'config' 以 JSON 格式写入到指定的配置文件路径中。
    如果写入过程中出现任何异常，将在终端打印 "save failed"。
    """
    try:
        config_path = os.path.join(MAIN_DIRECTORY, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("save failed")


# 全局配置变量
global config
config = DEFAULT_CONFIG.copy()


def load_config():
    """
    从 config.json 文件加载配置信息，如果文件不存在则创建默认配置文件。

    首先检查配置文件是否存在，如果存在则读取文件内容并更新到全局配置变量 'config' 中。
    如果读取过程中出现异常，将重置 'config' 为默认配置并保存。
    如果配置文件不存在，直接保存默认配置到文件中。
    """
    global config
    config_file_path = os.path.join(MAIN_DIRECTORY, "config.json")

    config_updated = False
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, "r", encoding="utf-8") as f:
                loaded_config = json.load(f)
                for key, value in DEFAULT_CONFIG.items():
                    if key not in loaded_config:
                        loaded_config[key] = value
                        config_updated = True
                config.update(loaded_config)
                if config_updated:
                    save_config()
        except Exception as e:
            config = DEFAULT_CONFIG.copy()
            save_config()
    else:
        save_config()


load_config()
output_handler = OutputHandler(
    language=config["LANGUAGE"], log_output=config["LOG_OUTPUT"]
)


def log_to_terminal(key, data=None, **kwargs):
    """
    将日志打印到终端。

    :param key: 翻译文本的 key，用于从输出处理器获取相应的翻译文本。
    :param data: 额外数据（可选），将在打印翻译文本后打印。
    :param kwargs: 动态参数，用于格式化翻译文本。
    只有当全局配置中的 'LOG_OUTPUT' 为 True 时，才会执行打印操作。
    """
    if config["LOG_OUTPUT"]:  # 仅当 LOG_OUTPUT 为 True 时才打印日志
        print("\n" + output_handler.get_translation("log_start"))  # 日志开头提示
        message = output_handler.get_translation(key, **kwargs)
        print(message)
        if data:
            print(data)


def log_to_web_ui(web_ui_url, key, data=None, **kwargs):
    """
    将日志发送到 WebUI。

    :param web_ui_url: WebUI 地址。
    :param key: 翻译文本的 key，用于从输出处理器获取相应的翻译文本。
    :param data: 额外数据（可选），将包含在发送到 WebUI 的负载中。
    :param kwargs: 动态参数，用于格式化翻译文本。
    如果未提供 'web_ui_url'，则函数直接返回，不执行任何操作。
    如果在发送过程中出现异常且 'LOG_OUTPUT' 为 True，将在终端打印错误信息。
    """
    if not web_ui_url:
        return
    try:
        import requests
        message = output_handler.get_translation(key, **kwargs)
        payload = {"message": message, "data": data}
        requests.post(web_ui_url, json=payload)
    except Exception as e:
        if config["LOG_OUTPUT"]:
            error_message = output_handler.get_translation(
                "log_web_ui_error", error=str(e)
            )
            print(error_message)


def run_main_program(user_input, web_ui_url=None, callback=False):
    api_key = config["API_KEY"]
    api_base_url = config["API_BASE_URL"]
    model = config["MODEL"]
    WEB_UI_URL = web_ui_url

    # 获取系统信息
    system_info = get_system_info()
    log_to_terminal("log_system_info", data=system_info)

    # 根据当前安全等级选择合适的参数
    execution_level = config["EXECUTION_LEVEL"]
    if execution_level == 0:
        from level.level_0 import get_prompt
    elif execution_level == 1:
        from level.level_1 import get_prompt
    elif execution_level == 2:
        from level.level_2 import get_prompt
    elif execution_level == 3:
        from level.level_3 import get_prompt
    else:
        raise ValueError(output_handler.get_translation("error_invalid_level"))

    # 生成 Prompt
    prompt = get_prompt(system_info)
    log_to_terminal("log_prompt_generated", prompt=prompt)

    # 获取 AI 响应
    ai_response = get_ai_response(
        prompt,
        api_key,
        api_base_url,
        model,
        user_input,
        config["TEMPERATURE"],
        config["MAX_TOKENS"],
        config["MAX_TURNS"],
        callback,
    )
    log_to_terminal("log_ai_response", data=ai_response)

    # 提取代码块
    code = extract_code(ai_response)
    log_to_terminal("log_code_extracted", data=code)

    # 如果检测到代码块，就直接执行并把执行结果拼到 ai_response 里
    if code:
        stdout, stderr = execute_in_subprocess(code, config, output_handler)
        if stderr:
            # 判断超时
            if "[TIMEOUT]" in stderr:
                error_text = output_handler.get_translation(
                    "error_timeout", timeout=config["RETURN_TIMEOUT"]
                )
                # 将错误信息直接拼到 ai_response
                ai_response += f"\n\n{error_text}"
                # append_to_last_history('\n\n'+error_text)
            else:
                error_text = output_handler.get_translation(
                    "error_execution", error=stderr
                )
                # 将错误信息直接拼到 ai_response
                ai_response += f"\n\n{error_text}"
                # append_to_last_history('\n\n'+error_text)
        else:
            # 如果执行没有错误，就把 stdout 拼到回复里
            if stdout and stdout.strip():
                ai_response += f"\n\n## {output_handler.get_translation('execution_result')}\n\n`{stdout.strip()}\n`"
                # append_to_last_history(output_handler.get_translation('execution_result')+stdout.strip())
            else:
                ai_response += f"\n\n## {output_handler.get_translation('no_stdout')}"
                # append_to_last_history(output_handler.get_translation('no_stdout'))

    # 回调逻辑：如AI中出现回调标识符，则提取回调内容再递归调用
    callback_text = extract_callback(ai_response)
    if callback_text:
        callback_result = run_main_program(callback_text, WEB_UI_URL, True)[
            "ai_response"
        ]

        ai_response += "\n\n" + callback_result

        # append_to_last_history(callback_result)

    # 准备返回结果
    result = {
        "prompt": prompt,  # 生成的提示
        "ai_response": ai_response
        or output_handler.get_translation("no_valid_response"),
        "error": None,
    }
    replace_last_history(ai_response)

    log_to_terminal("log_execution_result", data=result)
    log_to_web_ui(web_ui_url, "log_execution_result", data=result)

    return result


def display_banner():
    banner_lines = output_handler.get_translation("welcome_banner")
    if isinstance(banner_lines, list):  # 如果是列表，逐行打印
        for line in banner_lines:
            print(line)
    else:  # 如果意外是字符串，直接打印
        print(banner_lines)


def main():
    output_handler.set_language(config["LANGUAGE"])
    output_handler.print_to_console(
        "help_language_updated", language=config["LANGUAGE"]
    )
    display_banner()  # 显示横幅
    output_handler.print_to_console(
        "current_security_level", level=config["EXECUTION_LEVEL"]
    )
    output_handler.print_to_console("input_help")
    print("+==================================================+")

    def process_user_input():
        # 获取本地化的输入提示
        input_message = output_handler.get_translation("input_message") + "\n>"
        user_input = input(input_message).strip()
        if user_input.upper() == ".HELP":
            show_help(
                config,
                clear_console=output_handler.clear_console,
                save_config=save_config,
                output_handler=output_handler,
            )
        elif user_input.upper() == ".EXIT":
            cleanup_temp_dir()
            output_handler.print_to_console("program_exit")
            exit(0)
        else:
            result = run_main_program(user_input)
            ai_response = result.get(
                "ai_response", output_handler.get_translation("no_valid_response")
            )
            output_handler.print_to_console("ai_response")
            print(ai_response)
            execution_result = result.get("execution_result", "")
            if execution_result:
                output_handler.print_to_console("execution_result")
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(execution_result)
                print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print("+==================================================+")

    if config["LOOP"]:
        while True:
            process_user_input()
    else:
        process_user_input()
    cleanup_temp_dir()


if __name__ == "__main__":
    main()
