import requests
import json

def get_ai_response(prompt, api_key, api_base_url, model):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "权限等级说明：数字越小权限越高。"},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4096,
        "temperature": 0.7
    }
    response = requests.post(api_base_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"调用失败，状态码：{response.status_code}, 错误信息：{response.text}"
