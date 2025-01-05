import os
import json


def t(key, translations, **kwargs):
    """
    获取翻译文本，并支持占位符替换
    """
    text = translations.get(key, key)
    if isinstance(text, str):
        return text.format(**kwargs)  # 如果是字符串，进行格式化
    return text  # 如果是其他类型（如列表），直接返回


# 输出处理类
class OutputHandler:
    def __init__(self, language="en", log_output=False):
        # 获取主程序（main.py）所在目录
        self.main_dir = os.path.dirname(os.path.abspath(__file__))  # 确保基于文件位置
        self.language = language
        self.log_output = log_output
        self.translations = self.load_translations(language)

    def load_translations(self, language):
        """
        加载语言文件
        """
        try:
            # 使用 main.py 所在目录作为 locale 的基准路径
            locale_path = os.path.join(self.main_dir, "../locale", f"{language}.json")
            with open(locale_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Language file '{language}' not found. Defaulting to English.")
            # 尝试加载默认英文语言包
            default_locale_path = os.path.join(self.main_dir, "../locale", "en.json")
            try:
                with open(default_locale_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except FileNotFoundError:
                raise FileNotFoundError(
                    "Default language file 'en.json' not found in locale directory."
                )

    def set_language(self, new_language):
        self.language = new_language
        self.translations = self.load_translations(new_language)

    def get_translation(self, key, **kwargs):
        text = self.translations.get(key, f"[MISSING TRANSLATION: {key}]")
        return text.format(**kwargs)

    def print_to_console(self, key, **kwargs):
        message = self.get_translation(key, **kwargs)
        print(message)

    def list_available_languages(self):
        """
        列出 locale 文件夹下的所有语言文件及其名称
        """
        available_languages = []
        locale_dir = os.path.join(self.main_dir, "../locale")  # 基于主程序所在目录
        if not os.path.exists(locale_dir):
            print("Locale directory not found.")
            return available_languages

        for file in os.listdir(locale_dir):
            if file.endswith(".json"):
                language_code = os.path.splitext(file)[0]
                try:
                    with open(
                        os.path.join(locale_dir, file), "r", encoding="utf-8"
                    ) as f:
                        translations = json.load(f)
                        language_name = translations.get("language_name", language_code)
                        available_languages.append((language_code, language_name))
                except Exception as e:
                    print(f"Failed to load {file}: {e}")
        return available_languages

    def log(self, key, **kwargs):
        """
        打印日志信息（仅在 log_output 为 True 时启用）
        """
        if self.log_output:
            message = t(key, self.translations, **kwargs)
            print(f"[LOG] {message}")

    def clear_console(self):
        """
        清屏函数，跨平台支持
        """
        os.system("cls" if os.name == "nt" else "clear")

    def get_translation(self, key, **kwargs):
        """
        获取翻译文本并根据需要进行格式化
        """
        text = self.translations.get(key, key)
        if isinstance(text, list):
            # 如果是列表，直接返回，不进行格式化
            return text
        return t(key, self.translations, **kwargs)
