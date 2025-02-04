function countTokensGPT(text) {
    if (!text) return 0;

    // 1️⃣ **正则表达式分词**（模拟 GPT BPE 规则）
    const regex = /'s|'t|'re|'ve|'m|'ll|'d| ?\w+| ?[^\w\s]+|\s+(?!\S)/g;
    let tokens = text.match(regex) || [];

    let tokenCount = 0;

    tokens.forEach(token => {
        // 2️⃣ **处理中文**（GPT 计算时每个汉字 1 个 Token）
        if (/[\u4e00-\u9fa5]/.test(token)) {
            tokenCount += token.length; // 中文每个字符独立计数
        }
        // 3️⃣ **处理数字**（长数字可能会拆分）
        else if (/^\d+$/.test(token)) {
            tokenCount += Math.ceil(token.length / 4); // 数字每 4 个字符 1 Token
        }
        // 4️⃣ **处理长单词**（基于 GPT BPE 规则，长单词会拆分）
        else if (token.length > 6) {
            tokenCount += Math.ceil(token.length / 3); // 每 3 个字符 1 Token
        }
        // 5️⃣ **其他情况（单词、标点、特殊字符）**
        else {
            tokenCount += 1;
        }
    });

    return tokenCount;
}

function updateToken(textarea, tokenH1) {
    tokenH1.textContent = `Token < ${countTokensGPT(textarea.value)} >`;
}

document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.querySelector('textarea');
    const tokenH1 = document.querySelector('h1');

    if (textarea && tokenH1) {
        textarea.addEventListener('input', () => updateToken(textarea, tokenH1));
        updateToken(textarea, tokenH1); // 初始化时更新 Token 计数
    }
});