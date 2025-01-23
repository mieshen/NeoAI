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

// 添加/更新 none 元素到聊天气泡的最下方
function updateNoneElement(chatContainer) {
    // 查找是否已经存在 "none" 元素
    let existingNone = chatContainer.querySelector(".none");

    // 如果存在，先删除
    if (existingNone) {
        existingNone.remove();
    }

    // 创建新的 "none" 元素
    const noneElement = document.createElement("div");
    noneElement.className = "none";
    
    // 将它添加到最下面
    chatContainer.appendChild(noneElement);
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
    const baseCharDuration = 5; // 每个字符的基础时长
    const reductionFactor = 0.8; // 短文本的时长缩减系数
    const minDuration = 200; // 最短总时长（毫秒）
    const maxDuration = 10000; // 最长总时长（毫秒）
    const totalCharacters = content.length;

    // 动态计算总时长
    let totalDuration = totalCharacters * baseCharDuration;

    // 对短文本应用缩减
    if (totalCharacters < 50) {
        totalDuration *= reductionFactor;
    }

    // 限制总时长在 [minDuration, maxDuration] 之间
    totalDuration = Math.min(Math.max(totalDuration, minDuration), maxDuration);

    // 动态计算每个字符的显示间隔
    const typingSpeed = totalDuration / totalCharacters;
    let index = 0;
    let currentText = "";

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

    // 动画逻辑
    const typeText = setInterval(() => {
        if (index < content.length) {
            // 模拟逐字输出
            currentText += content.charAt(index);
            index++;

            // 渲染部分 Markdown 内容
            const renderedMarkdown = md.render(currentText);
            markdownContainer.innerHTML = renderedMarkdown;

            // 添加复制按钮
            addCopyButton(markdownContainer);

            // 滚动到最新消息
            bubble.parentNode.scrollTop = bubble.parentNode.scrollHeight;
        } else {
            clearInterval(typeText); // 动画结束
        }
    }, typingSpeed);
}

// 为渲染的代码块添加复制按钮
function addCopyButton(container) {
    // 获取所有的代码块
    const codeBlocks = container.querySelectorAll("pre code");

    codeBlocks.forEach((codeBlock) => {
        // 如果没有添加复制按钮，则添加
        if (!codeBlock.closest("pre").querySelector(".copy-btn")) {
            const button = document.createElement("button");
            button.classList.add("copy-btn");
            button.innerText = "复制";

            // 为按钮添加点击事件，复制代码到剪贴板
            button.addEventListener("click", () => {
                const text = codeBlock.textContent || codeBlock.innerText;
                copyToClipboard(text); // 执行复制操作
            });

            // 将按钮添加到代码块前面
            const preTag = codeBlock.closest("pre");
            preTag.insertBefore(button, preTag.firstChild);
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