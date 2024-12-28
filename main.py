import os
import subprocess
import tempfile
import shutil
import json  # 用于持久化配置
from utils.system_info import get_system_info
from utils.ai_interaction import get_ai_response
from level.operation_levels import operation_levels
from level.common import generate_prompt, extract_code

# === 配置常量 ===
CONFIG_FILE = os.path.join(os.getcwd(), "config.json")  # 配置文件路径
DEFAULT_CONFIG = {
    "API_KEY": "YOUR_API_KEY",
    "API_BASE_URL": "https://api.openai.com/v1/chat/completions",
    "MODEL": "gpt-4o",
    "EXECUTION_LEVEL": 0,
    "LOOP": True,
    "LOG_OUTPUT": False
}

# 全局配置变量
config = DEFAULT_CONFIG.copy()


def load_config():
    """
    从 config.json 加载配置
    如果配置文件不存在，创建一个默认配置文件
    """
    global config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config.update(json.load(f))
            print("配置文件加载成功！")
        except Exception as e:
            print(f"加载配置文件失败，使用默认配置: {e}")
    else:
        # 如果配置文件不存在，生成默认配置
        print("配置文件不存在，正在生成默认配置...")
        save_config()


def save_config():
    """
    将当前配置保存到 config.json
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("配置已保存到 config.json")
    except Exception as e:
        print(f"保存配置文件失败: {e}")


def clear_console():
    """
    清屏函数，跨平台支持
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('cls' if os.name == 'nt' else 'clear')


def log_to_terminal(data):
    """
    将日志打印到终端
    """
    if config["LOG_OUTPUT"]:  # 仅当 LOG_OUTPUT 为 True 时才打印日志
        print("\n日志记录：")
        print(data)


def log_to_web_ui(web_ui_url, data):
    """
    将日志发送到 WebUI
    """
    if not web_ui_url:
        return
    try:
        import requests
        requests.post(web_ui_url, json=data)
    except Exception as e:
        if config["LOG_OUTPUT"]:
            print(f"无法发送日志到 WebUI：{e}")


def execute_in_subprocess(code):
    temp_file_path = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()) + ".py")
    with open(temp_file_path, "w", encoding="utf-8") as temp_file:  # 确保使用 UTF-8 编码
        temp_file.write("# -*- coding: utf-8 -*-\n")  # 写入编码声明
        temp_file.write(code)

    try:
        process = subprocess.Popen(
            ["python", temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True
        )
        stdout, stderr = process.communicate()
        if stderr.strip():
            return stdout.strip(), stderr.strip()
        return stdout.strip(), None
    except Exception as e:
        return None, str(e)
    finally:
        try:
            os.remove(temp_file_path)
        except Exception as cleanup_error:
            pass


def cleanup_temp_dir():
    """
    清理临时文件夹
    """
    temp_dir = os.path.join(os.getcwd(), "temp_scripts")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def run_main_program(user_input, web_ui_url=None):


    api_key = config["API_KEY"]
    api_base_url = config["API_BASE_URL"]
    model = config["MODEL"]
    # 获取系统信息
    system_info = get_system_info()

    # 根据当前执行级别选择合适的参数
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
        raise ValueError("无效的执行级别")

    # 生成 Prompt
    prompt = get_prompt(user_input, system_info)

    # 获取 AI 响应
    ai_response = get_ai_response(prompt, api_key, api_base_url, model)

    # 提取代码块
    code = extract_code(ai_response)

    # 执行代码或返回普通响应
    execution_result = None
    if code:
        stdout, stderr = execute_in_subprocess(code)
        if stderr:  # 如果有错误输出
            execution_result = f"执行错误: {stderr}"
        else:
            execution_result = stdout if stdout else "无标准输出"
    else:
        execution_result = None

    # 构造返回数据
    result = {
        "prompt": prompt,
        "ai_response": ai_response if ai_response else "无有效响应",
        "execution_result": execution_result if execution_result and execution_result != ai_response else "",
        "error": None,
    }

    log_to_terminal(result)  # 打印到终端（受 LOG_OUTPUT 控制）
    log_to_web_ui(web_ui_url, result)  # 始终发送到 WebUI
    return result


def display_banner():
    print("+=========================================+")
    print(" ███╗   ██╗███████╗ ██████╗      █████╗ ██╗")
    print(" ████╗  ██║██╔════╝██╔═══██╗    ██╔══██╗██║")
    print(" ██╔██╗ ██║█████╗  ██║   ██║    ███████║██║")
    print(" ██║╚██╗██║██╔══╝  ██║   ██║    ██╔══██║██║")
    print(" ██║ ╚████║███████╗╚██████╔╝    ██║  ██║██║")
    print(" ╚═╝  ╚═══╝╚══════╝ ╚═════╝     ╚═╝  ╚═╝╚═╝")
    print("+=========================================+")


def show_help():
    """
    显示帮助信息并允许用户修改配置
    """
    GREEN = '\033[92m'  # 绿色
    RESET = '\033[0m'   # 重置颜色

    while True:
        clear_console()
        print("+=========== 帮助信息 ===========+")
        print(f" 1. 输入'{GREEN}.BASE_URL <url>{RESET}' 修改 API 地址")
        print(f" 2. 输入'{GREEN}.MODEL <model>{RESET}' 修改模型")
        print(f" 3. 输入'{GREEN}.KEY <key>{RESET}' 修改 API 密钥")
        print(f" 4. 输入'{GREEN}.LEVEL <level>{RESET}' 修改安全级别")
        print(f" 5. 输入'{GREEN}.SHOW_BASE_URL{RESET}' 查看当前 API 地址")
        print(f" 6. 输入'{GREEN}.SHOW_MODEL{RESET}' 查看当前模型")
        print(f" 7. 输入'{GREEN}.SHOW_KEY{RESET}' 查看当前 API 密钥")
        print(f" 8. 输入'{GREEN}.SHOW_LEVEL{RESET}' 查看当前安全级别")
        print(f" 9. 输入'{GREEN}.EXPLAIN_LEVELS{RESET}' 解释安全级别含义")
        print()
        print(f" 0. 输入'{GREEN}.BACK{RESET}' 返回聊天页面")
        print("+================================+")

        user_input = input("输入指令:").strip()

        if user_input.upper().startswith(".BASE_URL"):
            config["API_BASE_URL"] = user_input[len(".BASE_URL"):].strip()
            save_config()
            print(f"API 地址已更新为: {config['API_BASE_URL']}")
        elif user_input.upper().startswith(".MODEL"):
            config["MODEL"] = user_input[len(".MODEL"):].strip()
            save_config()
            print(f"模型已更新为: {config['MODEL']}")
        elif user_input.upper().startswith(".KEY"):
            config["API_KEY"] = user_input[len(".KEY"):].strip()
            save_config()
            print(f"API 密钥已更新。")
        elif user_input.upper().startswith(".LEVEL"):
            level = user_input[len(".LEVEL"):].strip()
            if level.isdigit() and 0 <= int(level) <= 3:
                config["EXECUTION_LEVEL"] = int(level)
                save_config()
                print(f"安全级别已更新为 Level {config['EXECUTION_LEVEL']}")
            else:
                print("无效的安全级别，请输入 0-3 的整数值。")
        elif user_input.upper() == ".SHOW_BASE_URL":
            print(f"当前 API 地址: {config['API_BASE_URL']}")
        elif user_input.upper() == ".SHOW_MODEL":
            print(f"当前模型: {config['MODEL']}")
        elif user_input.upper() == ".SHOW_KEY":
            print(f"当前 API 密钥: {config['API_KEY']}")
        elif user_input.upper() == ".SHOW_LEVEL":
            print(f"当前安全级别: Level {config['EXECUTION_LEVEL']}")
        elif user_input.upper() == ".EXPLAIN_LEVELS":
            explain_levels()
        elif user_input.upper() == ".BACK":
            clear_console()
            main()
            break
        else:
            print("无效指令，请重试。")
        input("\n按回车键继续...")  # 等待用户按回车继续


def explain_levels():
    """
    解释各个安全等级的含义
    """
    # ANSI 转义序列定义颜色
    RED = '\033[91m'      # 红色
    YELLOW = '\033[93m'   # 黄色
    BLUE = '\033[94m'     # 蓝色
    GREEN = '\033[92m'    # 绿色
    RESET = '\033[0m'     # 重置颜色

    clear_console()
    print("+==================安全等级说明==================+")
    print(f"{RED} Level 0: 最高权限{RESET}")
    print("   - 拥有所有权限，包括危险操作。")
    print("   - 包括但不限于：删除系统文件、修改分区表、定时关机。")
    print()
    print(f"{YELLOW} Level 1: 高权限{RESET}")
    print("   - 允许大多数系统操作，但禁止高危操作。")
    print("   - 包括但不限于：终止进程、修改文件权限、安装 pip 包。")
    print()
    print(f"{BLUE} Level 2: 中等权限{RESET}")
    print("   - 允许部分操作，限制系统修改和高危命令。")
    print("   - 包括但不限于：上传/下载文件、压缩文件、修改文件、打开浏览器。")
    print()
    print(f"{GREEN} Level 3: 低权限{RESET}")
    print("   - 仅允许只读和安全操作。")
    print("   - 包括但不限于：读取系统信息、列出目录内容。")
    print("+================================================+")


def main():
    load_config()  # 加载配置文件
    display_banner()
    print(f"* 当前安全等级 < Level {config['EXECUTION_LEVEL']} >")
    print("* 输入'.HELP' 查看帮助")
    print()

    def process_user_input():
        user_input = input("输入消息:").strip()

        if user_input.upper() == ".HELP":
            show_help()
        elif user_input.upper() == ".EXIT":
            print("程序已退出，感谢使用！")
            exit(0)
        else:
            result = run_main_program(user_input)
            ai_response = result.get("ai_response", "无有效响应")
            print("\nAI 响应：")
            print(ai_response)

            execution_result = result.get("execution_result", "")
            if execution_result:
                print("\n执行结果：")
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(execution_result)
                print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    if config["LOOP"]:
        while True:
            process_user_input()
    else:
        process_user_input()

    cleanup_temp_dir()


if __name__ == "__main__":
    main()
