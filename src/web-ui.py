import copy
import os
import subprocess
import threading
from flask import Flask, request, jsonify, render_template, send_from_directory
from main import run_main_program, load_config, config, save_config
from utils.output_handler import OutputHandler  # 导入 OutputHandler
from utils.ai_interaction import clear_history
from utils.ai_interaction import history
from main import VERSION

# 初始化 OutputHandler（默认语言：英语）
output_handler = OutputHandler(language=config["LANGUAGE"], log_output=True)

load_config()
# 指定 templates 和 static 文件夹路径
app = Flask(
    __name__,
    template_folder="web-ui/templates",  # 指定模板路径
    static_folder="web-ui/static",  # 指定静态文件路径
)

logs = []
port = 7820
docs_port = port + 1


@app.route("/debug/history", methods=["GET"])
def log_page():
    """
    以 HTML 页面形式显示日志
    """
    import json

    decoded_logs = []
    for log in logs:
        decoded_log = log.copy()
        if isinstance(log.get("full_log"), str):
            # 解码 full_log 中的 Unicode 转义字符
            decoded_log["full_log"] = json.loads(f'"{log["full_log"]}"')
        decoded_logs.append(decoded_log)
    return render_template("debug-history.html", logs=decoded_logs, history=history)


@app.template_filter("translate")
def translate(key, **kwargs):
    """
    根据全局语言设置动态获取翻译
    """
    output_handler.set_language(config["LANGUAGE"])
    return output_handler.get_translation(key, **kwargs)


@app.route("/")
def index():
    """
    WebUI 主页面
    """
    return render_template("index.html")


@app.route("/config")
def config_page():
    """
    配置管理页面
    """
    return render_template("config.html", config=config)


@app.route("/menu")
def menu():
    return render_template("menu.html", version=VERSION)


@app.route("/api/logs", methods=["GET"])
def get_logs():
    """
    返回实时日志数据
    """
    return jsonify(logs), 200


@app.route("/api/clear-history", methods=["GET"])
def clear_history_route():
    src_history = copy.deepcopy(history)
    clear_history()
    return (
        jsonify(
            {"message": "清除好啦~", "history": history, "src_history": src_history}
        ),
        200,
    )


@app.route("/api/interact", methods=["POST"])
def interact_with_ai():
    """
    与 AI 交互
    """
    data = request.json
    if not data or "user_input" not in data:
        return (
            jsonify({"error": output_handler.get_translation("missing_user_input")}),
            400,
        )

    user_input = data["user_input"]

    # 调用主程序处理请求
    result = run_main_program(user_input)

    ai_response = result.get("ai_response", "")

    # 添加完整日志信息
    logs.append(
        {"user_input": user_input, "ai_response": ai_response, "full_log": result}
    )

    return (
        jsonify(
            {
                "ai_response": ai_response,
                "execution_result": result.get("execution_result", "").strip(),
            }
        ),
        200,
    )


@app.route("/api/config", methods=["GET", "POST"])
def manage_config():
    """
    获取或更新配置
    """
    if request.method == "GET":
        return jsonify(config), 200

    elif request.method == "POST":
        new_config = request.json
        if not new_config:
            return (
                jsonify(
                    {
                        "error": output_handler.get_translation(
                            "invalid_configuration_data"
                        )
                    }
                ),
                400,
            )

        # 更新配置
        config.update(new_config)
        save_config()  # 保存配置到文件
        return (
            jsonify(
                {
                    "message": output_handler.get_translation(
                        "config_updated_successfully"
                    )
                }
            ),
            200,
        )


@app.route("/api/get-history", methods=["GET"])
def get_history():
    return jsonify(history), 200


def find_free_port():
    """
    动态分配未被占用的端口
    """


@app.route("/api/add-history", methods=["GET"])
def add_history():
    """
    根据请求的 type 参数（ai 或 user）添加一条历史记录。
    """
    record_type = request.args.get("type", "").lower()  # 获取 type 参数，转换为小写
    text = request.args.get("text", "")  # 获取 text 参数

    if not text:  # 检查 text 是否为空
        return jsonify({"error": "Missing 'text' parameter"}), 400

    if record_type not in ["ai", "user"]:  # 检查 type 是否有效
        return (
            jsonify(
                {"error": f"Invalid 'type': {record_type}. Must be 'ai' or 'user'."}
            ),
            400,
        )

    # 根据 type 添加历史记录
    history.append(
        {"role": "assistant" if record_type == "ai" else "user", "content": text}
    )

    return jsonify(
        {"message": "History updated successfully!", "current_history": history}
    )


@app.route("/set_language/<lang>", methods=["POST", "GET"])
def set_language(lang):
    config["LANGUAGE"] = lang
    save_config()

    output_handler.set_language(lang)

    return jsonify({"LANGUAGE": lang, "message": f"Language set to {lang}"}), 200


# 获取当前脚本的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # 脚本所在目录
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # 项目根目录（脚本目录的上一级）
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")  # docs 目录路径


def run_docs_server():
    """
    在新线程中运行 docs 目录的 HTTP 服务器
    """
    subprocess.run(["python", "-m", "http.server", str(docs_port)], cwd=DOCS_DIR)


# 在新线程中启动 docs 目录的 HTTP 服务器
threading.Thread(target=run_docs_server, daemon=True).start()


if __name__ == "__main__":
    load_config()  # 加载配置

    print(
        output_handler.get_translation(
            "starting_web_ui", port=port, docs_port=docs_port
        )
    )

    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
