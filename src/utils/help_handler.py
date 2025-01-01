def show_help(config, clear_console, save_config, output_handler):
    """
    显示帮助信息并允许用户修改配置
    """
    GREEN = '\033[92m'  # 绿色
    RESET = '\033[0m'   # 重置颜色

    while True:
        save_config()
        clear_console()

        # 获取帮助标题和选项内容
        help_title = output_handler.get_translation("help_title")
        help_options = output_handler.get_translation("help_options")

        print(help_title)
        for option in help_options:
            print(option.format(GREEN=GREEN, RESET=RESET))
        print()
        # 获取本地化的输入提示
        input_message = output_handler.get_translation("input_command")
        user_input = input(input_message).strip()

        if user_input.upper().startswith(".BASE_URL"):
            config["API_BASE_URL"] = user_input[len(".BASE_URL"):].strip()
            output_handler.print_to_console("help_base_url_updated", url=config["API_BASE_URL"])
        elif user_input.upper().startswith(".MODEL"):
            config["MODEL"] = user_input[len(".MODEL"):].strip()
            output_handler.print_to_console("help_model_updated", model=config["MODEL"])
        elif user_input.upper().startswith(".KEY"):
            config["API_KEY"] = user_input[len(".KEY"):].strip()
            output_handler.print_to_console("help_key_updated")
        elif user_input.upper().startswith(".LEVEL"):
            level = user_input[len(".LEVEL"):].strip()
            if level.isdigit() and 0 <= int(level) <= 3:
                config["EXECUTION_LEVEL"] = int(level)
                output_handler.print_to_console("help_level_updated", level=config["EXECUTION_LEVEL"])
            else:
                output_handler.print_to_console("help_invalid_level")
        elif user_input.upper().startswith(".RETURN_TIMEOUT"):
            timeout = user_input[len(".RETURN_TIMEOUT"):].strip()
            if timeout.isdigit() or timeout == "-1":
                config["RETURN_TIMEOUT"] = int(timeout)
                output_handler.print_to_console("help_timeout_updated", timeout=config["RETURN_TIMEOUT"])
            else:
                output_handler.print_to_console("help_invalid_timeout")
        elif user_input.upper().startswith(".TEMPERATURE"):
            temperature = user_input[len(".TEMPERATURE"):].strip()
            try:
                temp_value = float(temperature)
                if 0 <= temp_value <= 1:
                    config["TEMPERATURE"] = temp_value
                    output_handler.print_to_console("help_temperature_updated", temperature=config["TEMPERATURE"])
                else:
                    output_handler.print_to_console("help_invalid_temperature")
            except ValueError:
                output_handler.print_to_console("help_invalid_temperature")
        elif user_input.upper().startswith(".MAX_TOKENS"):
            max_tokens = user_input[len(".MAX_TOKENS"):].strip()
            if max_tokens.isdigit():
                config["MAX_TOKENS"] = int(max_tokens)
                output_handler.print_to_console("help_max_tokens_updated", max_tokens=config["MAX_TOKENS"])
            else:
                output_handler.print_to_console("help_invalid_max_tokens")
        elif user_input.upper().startswith(".MAX_TURNS"):
            max_turns = user_input[len(".MAX_TURNS"):].strip()
            if max_turns.isdigit():
                config["MAX_TURNS"] = int(max_turns)
                output_handler.print_to_console("help_max_turns_updated", max_turns=config["MAX_TURNS"])
            else:
                output_handler.print_to_console("help_invalid_max_turns")

        elif user_input.upper() == ".SHOW_BASE_URL":
            output_handler.print_to_console("help_show_base_url", url=config["API_BASE_URL"])
        elif user_input.upper() == ".SHOW_MODEL":
            output_handler.print_to_console("help_show_model", model=config["MODEL"])
        elif user_input.upper() == ".SHOW_KEY":
            output_handler.print_to_console("help_show_key", key=config["API_KEY"])
        elif user_input.upper() == ".SHOW_LEVEL":
            output_handler.print_to_console("help_show_level", level=config["EXECUTION_LEVEL"])
        elif user_input.upper() == ".SHOW_TIMEOUT":
            output_handler.print_to_console("help_show_timeout", timeout=config["RETURN_TIMEOUT"])
        elif user_input.upper() == ".SHOW_TEMPERATURE":
            output_handler.print_to_console("help_show_temperature", temperature=config["TEMPERATURE"])
        elif user_input.upper() == ".SHOW_MAX_TOKENS":
            output_handler.print_to_console("help_show_max_tokens", max_tokens=config["MAX_TOKENS"])
        elif user_input.upper() == ".SHOW_MAX_TURNS":
            output_handler.print_to_console("help_show_max_turns", max_turns=config["MAX_TURNS"])
        elif user_input.upper() == ".EXPLAIN_LEVELS":
            explain_levels(clear_console, output_handler)
        elif user_input.upper() == ".LANGUAGE":
            available_languages = output_handler.list_available_languages()
            print(output_handler.get_translation("available_languages"))
            for idx, (lang_code, lang_name) in enumerate(available_languages, start=1):
                print(f"{idx}. {lang_name} ({lang_code})")
            try:
                selection = int(input(output_handler.get_translation("select_language")).strip())
                if 1 <= selection <= len(available_languages):
                    selected_language = available_languages[selection - 1][0]
                    config["LANGUAGE"] = selected_language
                    output_handler.set_language(selected_language)
                    output_handler.print_to_console("help_language_updated", language=available_languages[selection - 1][1])

                else:
                    output_handler.print_to_console("help_invalid_language")
            except ValueError:
                output_handler.print_to_console("help_invalid_language")

        elif user_input.upper() == ".BACK":
            clear_console()
            break
        else:
            output_handler.print_to_console("help_invalid_command")

        # 获取本地化的继续提示
        continue_message = output_handler.get_translation("press_enter_to_continue")
        input(continue_message)



def explain_levels(clear_console, output_handler):
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

    # 获取安全等级说明标题和内容
    levels_title = output_handler.get_translation("levels_title")
    levels_description = output_handler.get_translation("levels_description")

    print(levels_title)
    for level in levels_description:
        print(level.format(RED=RED, YELLOW=YELLOW, BLUE=BLUE, GREEN=GREEN, RESET=RESET))
    print()
