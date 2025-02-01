import requests
import json

# 初始化历史记录
history = []


def get_ai_response(
    prompt,
    api_key,
    api_base_url,
    model,
    user_input,
    temperature,
    max_tokens,
    max_turns,
    callback=False,
):
    """
    调用 OpenAI API，并在调用成功时自动更新历史记录，支持设置最大聊天轮次。

    参数：
        prompt (str): 系统指令。
        api_key (str): API 密钥。
        api_base_url (str): API 基础 URL。
        model (str): 模型名称。
        user_input (str): 用户当前输入。
        temperature (float): 控制生成随机性。
        max_tokens (int): 最大生成 token 数。
        max_turns (int): 保存的最大对话轮次（1 轮 = 1 次用户输入 + AI 回复）。

    返回：
        str: AI 回复内容或错误信息。
    """
    global history  # 使用全局变量 history
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # 构造完整的 messages，包含固定的 prompt 和历史记录
    messages = (
        [{"role": "system", "content": prompt}]
        + history
        + [{"role": "user", "content": user_input}]
    )

    # 构造请求 payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        # 发起请求
        response = requests.post(
            api_base_url, headers=headers, data=json.dumps(payload), timeout=120
        )

        if response.status_code == 200:
            # 获取 AI 回复
            ai_response = response.json()["choices"][0]["message"]["content"]

            # 自动更新历史记录
            if not callback:
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": ai_response})

            # 限制历史记录长度，保持最多 max_turns 轮对话
            if len(history) > max_turns * 2:  # 每轮包含用户输入和 AI 回复，共 2 条
                history = history[-max_turns * 2 :]

            return ai_response
        else:
            return (
                f"调用失败，状态码：{response.status_code}, 错误信息：{response.text}"
            )

    except requests.exceptions.SSLError as ssl_error:
        return f"SSL 错误：{ssl_error}"

    except requests.exceptions.RequestException as req_error:
        return f"请求错误：{req_error}"

    except Exception as e:
        return f"未知错误：{e}"


def append_to_last_history(content_to_append):
    """
    将字符串拼接到 history 列表最后一个元素的 content 字段末尾。

    参数：
        content_to_append (str): 要拼接的字符串。
    """
    global history
    if history:  # 确保 history 不为空
        history[-1]["content"] += f"\n\n{content_to_append}"
    else:
        print("历史记录为空，无法拼接内容！")

# 替换 history 列表最后一个元素的 content 字段。
def replace_last_history(content_to_replace):
    """
    替换 history 列表最后一个元素的 content 字段。

    参数：
        content_to_replace (str): 要替换的字符串。
    """
    global history
    if history:  # 确保 history 不为空
        history[-1]["content"] = content_to_replace
    else:
        print("历史记录为空，无法替换内容！")


def clear_history():
    history.clear()
