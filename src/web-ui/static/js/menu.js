// 显示菜单
async function showMenu() {
    const overlay = document.getElementById("menuOverlay");
    overlay.classList.remove("hidden"); // 确保元素可见

    try {
        const response = await fetch("/menu"); // 加载菜单 HTML
        if (response.ok) {
            const htmlContent = await response.text();
            overlay.innerHTML = htmlContent;

            // 添加动画类
            overlay.classList.add("visible");
            const menuContainer = overlay.querySelector(".menu-container");
            if (menuContainer) {
                setTimeout(() => menuContainer.classList.add("visible"), 50); // 延迟以确保动画效果
            }
        } else {
            console.error("无法加载菜单页面");
        }
    } catch (error) {
        console.error("加载菜单页面出错:", error);
    }
}

// 关闭菜单
function closeMenu() {
    const overlay = document.getElementById("menuOverlay");
    const menuContainer = overlay.querySelector(".menu-container");

    // 移除动画类以触发淡出效果
    if (menuContainer) {
        menuContainer.classList.remove("visible");
    }

    overlay.classList.remove("visible");

    // 延迟清空内容，等待动画结束
    setTimeout(() => {
        overlay.classList.add("hidden");
        overlay.innerHTML = "";
    }, 300); // 与 CSS 的动画时间一致
}


function clearHistory() {
    const button = document.getElementById('clear-history-button');
    const originalText = button.innerHTML;
    button.innerHTML = '...';
    fetch('/api/clear-history', { method: 'GET' })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
        })
        .then(data => {
            console.log(data.message);
            button.innerHTML = '✅';
            setTimeout(() => {
                button.innerHTML = originalText;
            }, 2000);
        })
        .catch(error => {
            button.innerHTML = '❌';
            setTimeout(() => {
                button.innerHTML = originalText;
            }, 4000);
        });
}