import copy
import src
from flask import Flask, request, jsonify, render_template
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


@app.route("/log/history", methods=["GET"])
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
    return render_template("history-log.html", logs=decoded_logs, history=history)


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


@app.route("/api/clear_history", methods=["GET"])
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


@app.route("/api/log/get-history", methods=["GET"])
def get_history():
    return jsonify(history), 200


def find_free_port():
    """
    动态分配未被占用的端口
    """
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        return s.getsockname()[1]


@app.route("/set_language/<lang>", methods=["POST", "GET"])
def set_language(lang):
    config["LANGUAGE"] = lang
    save_config()

    output_handler.set_language(lang)

    return jsonify({"LANGUAGE": lang, "message": f"Language set to {lang}"}), 200


if __name__ == "__main__":
    load_config()  # 加载配置

    port = 7820
    print(output_handler.get_translation("starting_web_ui", port=port))

    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
