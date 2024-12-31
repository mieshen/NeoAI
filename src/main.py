import ast
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
    "EXECUTION_LEVEL": 2,
    "LOOP": True,
    "LOG_OUTPUT": False,
    "RETURN_TIMEOUT" : -1, # -1 为自适应超时，大于 0 为固定超时
    "TEMPERATURE": 0.7,
    "MAX_TOKENS": 4096,
    "MAX_TURNS": 32,

}

# 全局配置变量
config = DEFAULT_CONFIG.copy()


def load_config():
    """
    从脚本运行目录的 config.json 加载配置
    如果配置文件不存在，创建一个默认配置文件。
    如果配置文件缺少参数，自动补充缺失参数。
    """
    global config
    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    config_updated = False  # 标志是否需要更新配置文件

    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, "r", encoding="utf-8") as f:
                loaded_config = json.load(f)
                # 补充缺失的参数
                for key, value in DEFAULT_CONFIG.items():
                    if key not in loaded_config:
                        print(f"配置文件缺少参数 < {key} >，已补充默认值: < {value} >")
                        loaded_config[key] = value
                        config_updated = True  # 标记配置文件需要更新

                config.update(loaded_config)

                # 如果有更新，保存回配置文件
                if config_updated:
                    save_config()
            print("配置文件加载成功！")
        except Exception as e:
            print(f"加载配置文件失败，将使用默认配置覆盖原有的问题配置: {e}")
            config = DEFAULT_CONFIG.copy()  # 使用默认配置
            save_config()
    else:
        # 如果配置文件不存在，生成默认配置
        print("配置文件不存在，正在生成默认配置...")
        save_config()


def save_config():
    """
    将当前配置保存到脚本运行目录的 config.json
    """
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("配置已保存到脚本目录的 config.json")
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



def estimate_timeout(code):
    """
    根据代码复杂度动态计算超时时间，优化简单语句和重复语句的权重
    """
    try:
        # 解析代码为 AST（抽象语法树）
        tree = ast.parse(code)
        
        # 基础时间和权重
        base_timeout = 5  # 基础超时时间
        statement_weight = 0.5  # 默认语句权重
        simple_call_weight = 0.1  # 简单函数调用权重
        loop_weight = 2  # 循环结构权重
        total_complexity = base_timeout

        # 定义常见简单函数集合
        simple_functions = {"print", "len", "input", "range", "str", "int", "float", "bool", "list", "dict", "set", "tuple"}

        # 遍历 AST，计算复杂度
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                total_complexity += loop_weight
            elif isinstance(node, (ast.If, ast.FunctionDef)):
                total_complexity += statement_weight
            elif isinstance(node, ast.Call):
                # 如果是简单的调用（如 print），降低权重
                if isinstance(node.func, ast.Name) and node.func.id in simple_functions:
                    total_complexity += simple_call_weight
                else:
                    total_complexity += statement_weight
            elif isinstance(node, ast.Assign):
                total_complexity += statement_weight
        
        # 返回计算的超时时间，确保至少为 5 秒
        return max(5, total_complexity)
    except Exception as e:
        # 如果代码解析失败，返回默认超时时间
        return 10


def execute_in_subprocess(code):
    """
    在脚本运行目录的 temp_scripts 文件夹中创建临时文件并执行代码，支持全局超时设置
    """
    try:
        # 使用全局变量确定超时时间
        if config["RETURN_TIMEOUT"] < 0:
            timeout = estimate_timeout(code)  # 自适应超时
        else:
            timeout = config["RETURN_TIMEOUT"]  # 使用固定超时
        
        # 获取脚本运行目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 构造 temp_scripts 文件夹路径
        temp_scripts_dir = os.path.join(script_dir, "temp_scripts")
        
        # 如果 temp_scripts 文件夹不存在，则创建
        if not os.path.exists(temp_scripts_dir):
            os.makedirs(temp_scripts_dir)
        
        # 创建临时 Python 文件
        temp_file_path = os.path.join(temp_scripts_dir, next(tempfile._get_candidate_names()) + ".py")
        with open(temp_file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write("# -*- coding: utf-8 -*-\n")
            temp_file.write(code)
        
        # 执行临时文件
        process = subprocess.Popen(
            ["python", temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True
        )
        
        try:
            # 设置超时并等待输出
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            # 如果超时，则终止子进程
            process.kill()
            return None, f"[TIMEOUT] 执行超时设定的 {timeout:.2f} 秒，已自动结束。"

        # 返回输出和错误信息
        if stderr.strip():
            return stdout.strip(), stderr.strip()
        return stdout.strip(), None
    except Exception as e:
        return None, f"[ERROR] {str(e)}"



def cleanup_temp_dir():
    """
    清理脚本运行目录下的 temp_scripts 文件夹
    """
    # 获取脚本运行目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(script_dir, "temp_scripts")
    
    # 检查文件夹是否存在
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def run_main_program(user_input, web_ui_url=None):


    api_key = config["API_KEY"]
    api_base_url = config["API_BASE_URL"]
    model = config["MODEL"]
    # 获取系统信息
    system_info = get_system_info()

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
        raise ValueError("无效的安全等级")

    # 生成 Prompt
    prompt = get_prompt(system_info)

    # 获取 AI 响应
    ai_response = get_ai_response(prompt, api_key, api_base_url, model, user_input, config["TEMPERATURE"], config["MAX_TOKENS"],config["MAX_TURNS"])

    # 提取代码块
    code = extract_code(ai_response)

    # 执行代码或返回普通响应
    execution_result = None
    if code:
        stdout, stderr = execute_in_subprocess(code)
        if stderr:  # 如果有错误输出
            if "[TIMEOUT]" in stderr:  # 检测是否为超时错误
                execution_result = f"{stderr}"
            else:
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
            cleanup_temp_dir()
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
