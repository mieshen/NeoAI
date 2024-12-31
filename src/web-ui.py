from flask import Flask, request, jsonify, render_template
from main import run_main_program, load_config, config, save_config

# 指定 templates 和 static 文件夹路径
app = Flask(
    __name__,
    template_folder="web-ui/templates",  # 指定模板路径
    static_folder="web-ui/static"       # 指定静态文件路径
)

logs = []

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
    return render_template("menu.html")


@app.route("/api/logs", methods=["GET"])
def get_logs():
    """
    返回实时日志数据
    """
    return jsonify(logs), 200


@app.route("/api/interact", methods=["POST"])
def interact_with_ai():
    """
    与 AI 交互
    """
    data = request.json
    if not data or "user_input" not in data:
        return jsonify({"error": "Missing user_input"}), 400

    user_input = data["user_input"]
    
    # 调用主程序处理请求
    result = run_main_program(user_input)

    # 提取简化的 AI 响应（例如权限提示）    
    ai_response = result.get("ai_response", "")

    # 添加完整日志信息
    logs.append({
        "user_input": user_input,
        "ai_response": ai_response,
        "full_log": result  
    })

    return jsonify({
        "ai_response": ai_response, 
        "execution_result": result.get("execution_result", "").strip()
    }), 200


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
            return jsonify({"error": "Invalid configuration data"}), 400 # 返回错误消息
        
        # 更新配置
        config.update(new_config)
        save_config()  # 保存配置到文件
        return jsonify({"message": "Configuration updated successfully!"}), 200 # 返回成功消息


def find_free_port():
    """
    动态分配未被占用的端口
    """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        return s.getsockname()[1]


if __name__ == "__main__":
    load_config()  # 加载配置
    # 使用动态端口
    port = 7820
    print(f"Starting WebUI on http://0.0.0.0:{port}...")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
