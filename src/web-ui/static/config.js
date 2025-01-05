function saveConfig() {
    const form = document.getElementById("config_form");
    const formData = new FormData(form);
    const updateButton = document.getElementById("update_button");

    const config = {};
    formData.forEach((value, key) => {
        if (key === "EXECUTION_LEVEL" || key === "MAX_TOKENS" || key === "MAX_TURNS") {
            config[key] = parseInt(value, 10); // 转换为整数
        } else if (key === "RETURN_TIMEOUT") {
            config[key] = parseFloat(value); // 转换为浮点数
        } else if (key === "TEMPERATURE") {
            if (value < 0) {
                config[key] = 0; // 温度不能为负数
            } else if (value > 2) {
                config[key] = 2; // 温度不能大于 2
            } else {
                config[key] = parseFloat(value);
            }
        } else if (value === "on") {
            config[key] = true; // 处理布尔值
        } else if (value === "off") {
            config[key] = false; // 处理布尔值关闭情况
        } else {
            config[key] = value; // 默认作为字符串保存
        }
    });

    // 处理语言选择框的值
    const languageSelect = document.getElementById("language_select");
    if (languageSelect) {
        config["LANGUAGE"] = languageSelect.value; // 获取语言选择框的值
    }

    fetch("/api/config", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(config),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to save configuration.");
            }
            return response.json();
        })
        .then((data) => {
            updateButton.textContent = "✅已更新配置文件✅"; // 更新按钮文本
            setTimeout(() => {
                updateButton.textContent = "保存配置"; // 恢复按钮文本
            }, 4000);

            // 如果语言发生改变，则刷新页面
            if (config["LANGUAGE"] !== data["LANGUAGE"]) {
                location.reload(); // 刷新页面以应用新的语言
            }
        })
        .catch((error) => {
            console.error("Error:", error);

            updateButton.textContent = "❌配置文件保存失败❌"; // 更新按钮文本
            setTimeout(() => {
                updateButton.textContent = "保存配置"; // 恢复按钮文本
            }, 6000);
        });
}


function changeLanguage() {
    const languageSelect = document.getElementById("language_select");
    const selectedLanguage = languageSelect.value;

    fetch(`/set_language/${selectedLanguage}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to change language.");
            }
            return response.json();
        })
        .then(() => {
            location.reload(); // 刷新页面以应用新的语言
        })
        .catch((error) => {
            console.error("Error changing language:", error);
        });
}


function togglePasswordVisibility() {
    const passwordInput = document.getElementById("api_key");
    const toggleButton = document.getElementById("toggle_password");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleButton.textContent = "隐藏隐私项🙈"; // 图标切换为隐藏状态
    } else {
        passwordInput.type = "password";
        toggleButton.textContent = "查看隐私项👁️"; // 图标切换为显示状态
    }
}
