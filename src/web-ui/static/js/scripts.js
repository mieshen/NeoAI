const header = document.querySelector(".header");
const movementLimit = 35;
const rotationLimit = 30;
let detectionArea = {};

function initializeDetectionArea() {
    const headerRect = header.getBoundingClientRect();
    const expansion = 50;

    detectionArea = {
        top: headerRect.top - expansion,
        left: headerRect.left - expansion,
        bottom: headerRect.bottom + expansion,
        right: headerRect.right + expansion,
    };
}

initializeDetectionArea();



let animationFrameId;
document.addEventListener("mousemove", (event) => {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }

    animationFrameId = requestAnimationFrame(() => {
        const isInsideDetectionArea =
            event.clientX >= detectionArea.left &&
            event.clientX <= detectionArea.right &&
            event.clientY >= detectionArea.top &&
            event.clientY <= detectionArea.bottom;

        if (isInsideDetectionArea) {
            const centerX = (detectionArea.left + detectionArea.right) / 2;
            const centerY = (detectionArea.top + detectionArea.bottom) / 2;

            const mouseX =
                (event.clientX - centerX) / (detectionArea.right - detectionArea.left);
            const mouseY =
                (event.clientY - centerY) / (detectionArea.bottom - detectionArea.top);

            const offsetX = -mouseX * movementLimit;
            const offsetY = -mouseY * movementLimit;

            const rotationX = mouseY * -rotationLimit; // 上下方向旋转
            const rotationY = -mouseX * -rotationLimit; // 左右方向旋转

            header.style.transform = `
                translate(${offsetX}px, ${offsetY}px)
                rotateX(${rotationX}deg)
                rotateY(${rotationY}deg)
            `;
        } else {
            header.style.transform = "translate(0, 0) rotateX(0deg) rotateY(0deg)";
        }
    });
});


function addChatBubble(content, isUser = false, bubbleId = null, skipAnimation = false) {
    const chatContainer = document.getElementById("chat_container");
    let bubble;

    if (bubbleId) {
        bubble = document.getElementById(bubbleId);
        if (bubble) {
            bubble.innerHTML += `<br>${content}`;
            return;
        }
    }

    bubble = document.createElement("div");
    bubble.className = `chat-bubble ${isUser ? "user-bubble" : "ai-bubble"}`;
    bubble.id = bubbleId || `bubble_${Date.now()}`;

    bubble.style.opacity = 0;
    bubble.innerHTML = ""; // 初始化为空

    chatContainer.appendChild(bubble);

    setTimeout(() => {
        bubble.style.opacity = 1;

        if (skipAnimation) {
            if (isUser) {
                // 用户输入直接渲染为纯文本
                bubble.innerText = content;
            } else {
                // AI 响应解析为 Markdown
                simulateTypingAnimation(bubble, content, true);
            }
        } else {
            if (isUser) {
                bubble.innerText = content;
            } else {
                simulateTypingAnimation(bubble, content);
            }
        }

        // 滚动到最新消息
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // 结束聊天时添加/更新 "none" 元素
        updateNoneElement(chatContainer);
    }, 300);

    return bubble.id;
}

// 添加/更新 none 元素到聊天气泡的顶部和底部
function updateNoneElement(chatContainer) {
    // 检查是否已存在顶部的 "none" 元素
    let topNone = chatContainer.querySelector(".none-top");
    if (!topNone) {
        // 如果顶部的 "none" 不存在，创建一个并添加到顶部
        topNone = document.createElement("div");
        topNone.className = "none none-top";
        chatContainer.insertBefore(topNone, chatContainer.firstChild); // 添加到最顶部
    }

    // 检查是否已存在底部的 "none" 元素
    let bottomNone = chatContainer.querySelector(".none-bottom");
    if (bottomNone) {
        // 如果底部的 "none" 存在，删除旧的
        bottomNone.remove();
    }

    // 创建新的底部 "none" 元素
    const newBottomNone = document.createElement("div");
    newBottomNone.className = "none none-bottom";

    // 添加到最底部
    chatContainer.appendChild(newBottomNone);
}


// 用于交互时处理用户输入的函数
function interact() {
    const userInputElement = document.getElementById("user_input");
    const sendButton = document.querySelector(".btn.btn-primary");

    if (!userInputElement.value.trim()) return;

    // 禁用输入框和发送按钮
    userInputElement.disabled = true;
    sendButton.disabled = true;

    // 发送用户输入内容
    addChatBubble(userInputElement.value, true);

    // 发送请求
    axios
        .post("/api/interact", { user_input: userInputElement.value })
        .then((response) => {
            const aiResponse = response.data.ai_response || "Error: No response from AI.";
            const executionResult = response.data.execution_result || "";

            // 确保 "执行结果：" 只有在 executionResult 有效时才显示
            let aiContent = aiResponse;
            if (executionResult.trim() && executionResult !== "No execution result returned." && executionResult.trim() !== "") {
                aiContent += `\n\n\n${executionResult}`;
            }

            // 添加 AI 响应的对话气泡
            addChatBubble(aiContent, false);
        })
        .catch((error) => {
            const errorMsg = error.response
                ? error.response.data
                : "Error: " + error.message;
            addChatBubble(`<pre>${JSON.stringify(errorMsg, null, 2)}</pre>`, false);
        })
        .finally(() => {
            // 恢复输入框和发送按钮的状态
            userInputElement.disabled = false;
            sendButton.disabled = false;

            // 清空输入框并重置高度
            userInputElement.value = "";
            userInputElement.style.height = "auto";  // 重置输入框的高度
        });
}



// 配置 highlight.js
hljs.configure({ languages: ["python", "javascript", "html", "css"] });

// 确保代码块高亮正确应用
document.querySelectorAll("pre code").forEach((el) => {
    hljs.highlightElement(el);
});



const md = window.markdownit({
    highlight: function (code, lang) {
        if (hljs.getLanguage(lang)) {
            return hljs.highlight(lang, code).value;
        }
        return hljs.highlightAuto(code).value;
    },
    html: true, // 允许渲染 HTML
    linkify: true, // 自动将 URL 转换为链接
});

function simulateTypingAnimation(bubble, content, skipAnimation = false) {
    // 清空对话气泡内容
    bubble.innerHTML = "";
    const markdownContainer = document.createElement("div");
    bubble.appendChild(markdownContainer);

    if (skipAnimation) {
        // 如果跳过动画，直接显示所有内容
        markdownContainer.innerHTML = md.render(content);
        addCopyButton(markdownContainer); // 添加复制按钮
        return;
    }

    const minDuration = 200; // 最短总时长（毫秒）
    const maxDuration = 10000; // 最长总时长（毫秒）
    const totalCharacters = content.length;

    // 动态计算总时长，限制在 [minDuration, maxDuration] 之间
    const totalDuration = Math.min(Math.max(totalCharacters * 5, minDuration), maxDuration);

    // 动态计算每个字符的显示间隔
    const typingSpeed = totalDuration / totalCharacters;

    // 动态调整每次显示的字符数
    let batchSize = 1; // 默认逐字输出
    if (typingSpeed < 10) {
        // 如果间隔时间太短，就批量显示多个字符
        batchSize = Math.ceil(10 / typingSpeed);
    }

    let index = 0;
    let currentText = "";

    const typeText = setInterval(() => {
        if (index < content.length) {
            // 批量增加字符
            currentText += content.slice(index, index + batchSize);
            index += batchSize;

            // 渲染部分 Markdown 内容
            markdownContainer.innerHTML = md.render(currentText);

            // 如果当前是最底部则滚动到最新消息
            bubble.parentNode.scrollTop = bubble.parentNode.scrollHeight;
        } else {
            clearInterval(typeText); // 动画结束
            addCopyButton(markdownContainer); // 添加复制按钮
        }
    }, Math.max(typingSpeed, 10)); // 确保每次间隔至少为 10ms
}

function addCopyButton(container) {
    // 获取所有的代码块
    const codeBlocks = container.querySelectorAll("pre code");

    codeBlocks.forEach((codeBlock) => {
        // 如果没有添加复制按钮，则添加
        if (!codeBlock.closest("pre").querySelector(".copy-btn")) {
            // 创建按钮
            const button = document.createElement("button");
            button.classList.add("copy-btn");
            button.innerText = "复制";

            // 为按钮添加点击事件，复制代码到剪贴板
            button.addEventListener("click", () => {
                const text = codeBlock.textContent || codeBlock.innerText;
                copyToClipboard(text); // 执行复制操作
                button.innerText = "已复制!";
                setTimeout(() => (button.innerText = "复制"), 2000); // 恢复按钮文字
            });

            // 将代码块的父元素设置为相对定位
            const preTag = codeBlock.closest("pre");
            preTag.style.position = "relative"; // 确保按钮可以相对于代码块定位

            // 设置按钮的样式
            button.style.position = "absolute";
            button.style.top = "10px"; // 距离代码块顶部的距离
            button.style.right = "10px"; // 距离代码块右边的距离
            button.style.zIndex = "10"; // 保证按钮不会被代码块覆盖
            button.style.padding = "5px 10px"; // 按钮样式优化
            button.style.fontSize = "12px";
            button.style.cursor = "pointer";

            // 添加按钮到代码块的父元素
            preTag.appendChild(button);
        }
    });
}

function copyToClipboard(text) {
    // 去掉顶部和底部的换行符
    const trimmedText = text.trim();

    // 去掉顶部的 >>>RUN>>> 和底部的 <<<RUN<<<
    const cleanedText = (trimmedText.replace(/^>>>RUN>>>/g, '').replace(/<<<RUN<<<$/g, '')).trim();
    let tempTextArea = document.createElement("textarea");  // 改成 let，允许重新赋值
    tempTextArea.value = cleanedText;  // 使用清理后的文本
    document.body.appendChild(tempTextArea);
    tempTextArea.select();
    document.execCommand("copy");
    document.body.removeChild(tempTextArea);
}






// 实际交互函数
function interact() {
    const userInputElement = document.getElementById("user_input");
    const sendButton = document.querySelector(".btn.btn-primary");

    if (!userInputElement.value.trim()) return;

    // 禁用输入框和发送按钮
    userInputElement.disabled = true;
    sendButton.disabled = true;

    // 发送用户输入内容
    addChatBubble(userInputElement.value, true);

    // 发送请求
    axios
        .post("/api/interact", { user_input: userInputElement.value })
        .then((response) => {
            const aiResponse = response.data.ai_response || "Error: No response from AI.";
            const executionResult = response.data.execution_result || "";

            // 确保 "执行结果：" 只有在 executionResult 有效时才显示
            let aiContent = aiResponse;
            if (executionResult.trim() && executionResult !== "No execution result returned." && executionResult.trim() !== "") {
                aiContent += `\n\n\n${executionResult}`;
            }

            // 添加 AI 响应的对话气泡
            addChatBubble(aiContent, false);
        })
        .catch((error) => {
            const errorMsg = error.response
                ? error.response.data
                : "Error: " + error.message;
            addChatBubble(`<pre>${JSON.stringify(errorMsg, null, 2)}</pre>`, false);
        })
        .finally(() => {
            // 恢复输入框和发送按钮的状态
            userInputElement.disabled = false;
            sendButton.disabled = false;

            // 清空输入框并重置高度
            userInputElement.value = "";
            userInputElement.style.height = "auto";  // 重置输入框的高度
        });
}

function adjustHeight(element) {
    element.style.height = "auto"; // 重置高度，防止高度累加
    const scrollHeight = element.scrollHeight; // 获取内容高度
    const maxHeight = parseInt(window.getComputedStyle(element).maxHeight); // 获取最大高度

    if (scrollHeight > maxHeight) {
        element.style.height = maxHeight + "px"; // 达到最大高度时固定为最大高度
    } else {
        element.style.height = scrollHeight + "px"; // 否则根据内容调整高度
    }
}

// 页面加载时加载历史记录
document.addEventListener("DOMContentLoaded", () => {
    axios
        .get("/api/get-history")
        .then((response) => {
            const logs = response.data; // 获取历史记录
            if (logs && logs.length > 0) {
                logs.forEach((log) => {
                    if (log.role === "user") {
                        // 如果是用户输入，直接渲染为纯文本
                        addChatBubble(log.content, true, null, true);
                    } else if (log.role === "assistant") {
                        // 如果是 AI 响应，解析为 Markdown
                        const responseData = {
                            ai_response: log.content,
                            execution_result: log.execution_result || "",
                        };

                        simulateInteractResponse(responseData);
                    }
                });

                // 滚动到最新消息
                const chatContainer = document.getElementById("chat_container");
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        })
        .catch((error) => {
            console.error("Error loading logs:", error);
        });
});


function simulateInteractResponse(responseData) {
    const aiResponse = responseData.ai_response || "Error: No response from AI.";
    const executionResult = responseData.execution_result || "";

    let aiContent = aiResponse;
    if (executionResult.trim() && executionResult !== "No execution result returned.") {
        aiContent += `\n\n\n${executionResult}`;
    }

    addChatBubble(aiContent, false, null, true);
}