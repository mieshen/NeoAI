function saveConfig() {
    const form = document.getElementById("config_form");
    const formData = new FormData(form);
    const updateButton = document.getElementById("update_button");

    const config = {};
    formData.forEach((value, key) => {
        if (key === "EXECUTION_LEVEL") {
            config[key] = parseInt(value, 10); // 一定要转换为10进制整数！！！否则后端会出现未知安全等级
        } else if (value === "on") {
            config[key] = true; // 处理布尔值
        } else if (value === "off") {
            config[key] = false; // 如果需要处理 "off" 情况
        } else {
            config[key] = value; // 默认作为字符串保存
        }
    });

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
    })
    .catch((error) => {
        console.error("Error:", error);

        updateButton.textContent = "❌配置文件保存失败❌"; // 更新按钮文本
        setTimeout(() => {
            updateButton.textContent = "保存配置"; // 恢复按钮文本
        }, 6000);
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
