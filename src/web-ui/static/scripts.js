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


function addChatBubble(content, isUser = false, bubbleId = null) {
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

        if (isUser) {
            bubble.innerText = content;
        } else {
            // 使用模拟打字动画渲染内容
            simulateTypingAnimation(bubble, content);
        }

        // 滚动到最新消息
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 300);

    return bubble.id;
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

function simulateTypingAnimation(bubble, content) {
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

    // 动画逻辑
    const typeText = setInterval(() => {
        if (index < content.length) {
            // 模拟逐字输出
            currentText += content.charAt(index);
            index++;

            // 渲染部分 Markdown 内容
            const renderedMarkdown = md.render(currentText);
            markdownContainer.innerHTML = renderedMarkdown;

            // 滚动到最新消息
            bubble.parentNode.scrollTop = bubble.parentNode.scrollHeight;
        } else {
            clearInterval(typeText); // 动画结束
        }
    }, typingSpeed);
}

function interact() {
    const userInputElement = document.getElementById("user_input");
    const sendButton = document.querySelector(".btn.btn-primary");

    if (!userInputElement.value.trim()) return;

    userInputElement.disabled = true;
    sendButton.disabled = true;

    addChatBubble(userInputElement.value, true);

    axios
        .post("/api/interact", { user_input: userInputElement.value })
        .then((response) => {
            const aiResponse = response.data.ai_response || "无有效响应";
            const executionResult = response.data.execution_result || "";

            let aiContent = aiResponse;
            if (executionResult.trim()) {
                if (!executionResult.includes("[NONE]")) {
                    //aiContent += "\n" + `<br>\n<b>执行结果:</b> ${executionResult}`;
                }
            }
            addChatBubble(aiContent, false);
        })
        .catch((error) => {
            const errorMsg = error.response
                ? error.response.data
                : "Error: " + error.message;
            addChatBubble(`<pre>${JSON.stringify(errorMsg, null, 2)}</pre>`, false);
        })
        .finally(() => {
            userInputElement.disabled = false;
            sendButton.disabled = false;
            userInputElement.value = "";
        });
}
