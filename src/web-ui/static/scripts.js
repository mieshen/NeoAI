

const header = document.querySelector('.header');
const movementLimit = 30; 
let detectionArea = {}; 


function initializeDetectionArea() {
    const headerRect = header.getBoundingClientRect(); 
    const expansion = 50; 

    detectionArea = {
        top: headerRect.top - expansion,
        left: headerRect.left - expansion,
        bottom: headerRect.bottom + expansion,
        right: headerRect.right + expansion
    };
}


initializeDetectionArea();


document.addEventListener('mousemove', (event) => {
    
    const isInsideDetectionArea =
        event.clientX >= detectionArea.left &&
        event.clientX <= detectionArea.right &&
        event.clientY >= detectionArea.top &&
        event.clientY <= detectionArea.bottom;

    if (isInsideDetectionArea) {
        
        const centerX = (detectionArea.left + detectionArea.right) / 2;
        const centerY = (detectionArea.top + detectionArea.bottom) / 2;

        const mouseX = (event.clientX - centerX) / (detectionArea.right - detectionArea.left);
        const mouseY = (event.clientY - centerY) / (detectionArea.bottom - detectionArea.top);

        const offsetX = -mouseX * movementLimit; 
        const offsetY = -mouseY * movementLimit; 

        header.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
    } else {
        
        header.style.transform = 'translate(0, 0)';
    }
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
    bubble.innerHTML = ""; 

    
    chatContainer.appendChild(bubble);

    
    setTimeout(() => {
        bubble.style.opacity = 1; 

        if (isUser) {
            
            bubble.innerText = content;
        } else {

            const markdownContent = marked.parse(content, {
                highlight: function (code, lang) {
                    if (hljs.getLanguage(lang)) {
                        return hljs.highlight(lang, code).value;
                    }
                    return hljs.highlightAuto(code).value;
                },
                gfm: true,
            });
            
            simulateTypingAnimation(bubble, markdownContent);
        }

        
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 300); 

    return bubble.id; 
}
hljs.configure({ languages: ['python', 'javascript', 'html', 'css'] });
document.querySelectorAll('pre code').forEach((el) => {
    hljs.highlightElement(el);
});



function simulateTypingAnimation(bubble, content) {
    const typingSpeed = 10; 
    let index = 0;
    let currentText = ""; 

    
    bubble.innerHTML = ""; 
    const markdownContainer = document.createElement("div");
    bubble.appendChild(markdownContainer);

    
    const typeText = setInterval(() => {
        if (index < content.length) {
            const nextChar = content.charAt(index);

            
            if (nextChar === "<") {
                
                const htmlEndIndex = content.indexOf(">", index);
                if (htmlEndIndex !== -1) {
                    currentText += content.slice(index, htmlEndIndex + 1); 
                    index = htmlEndIndex + 1; 
                } else {
                    currentText += nextChar; 
                    index++;
                }
            } else {
                
                currentText += nextChar;
                index++;
            }

            
            const renderedMarkdown = marked.parse(currentText); 
            markdownContainer.innerHTML = renderedMarkdown; 

            
            bubble.parentNode.scrollTop = bubble.parentNode.scrollHeight;
        } else {
            clearInterval(typeText); 
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

    
    axios.post("/api/interact", { user_input: userInputElement.value })
        .then(response => {
            const aiResponse = response.data.ai_response || "无有效响应"; 
            const executionResult = response.data.execution_result || ""; 

            
            let aiContent = aiResponse;
            if (executionResult.trim()) {
                if (executionResult.trim() !== "无标准输出") {
                    aiContent += '\n' + `<br><b>执行结果:</b> ${executionResult}`;
                }
            }
            addChatBubble(aiContent, false); 
        })
        .catch(error => {
            const errorMsg = error.response ? error.response.data : "Error: " + error.message;
            addChatBubble(`<pre>${JSON.stringify(errorMsg, null, 2)}</pre>`, false); 
        })
        .finally(() => {
            
            userInputElement.disabled = false;
            sendButton.disabled = false; 
            userInputElement.value = ""; 
        });
}
