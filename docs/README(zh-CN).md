# NeoAI：无需一行代码！让 AI 掌控您的电脑！

<p align="center">
  <img src="images/LOGO.png" alt="Logo" width="400" />
</p>

## [Web 文档](thed0ublec.github.com/NeoAI)

<section align="center">
  <img src="https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge" alt="Windows Support">
  <img src="https://img.shields.io/badge/platform-macOS-lightgreen?style=for-the-badge" alt="macOS Support">
  <img src="https://img.shields.io/badge/platform-Linux-green?style=for-the-badge" alt="Linux Support">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License">
</section>

---

前言：NeoAI 目前正在测试阶段，有许多未知的问题。

如果你愿意的话，可以成为 NeoAI 的贡献者，让我们一起完善 NeoAI！

---

## **目录**

- [NeoAI 的功能](#neoai-的功能)
- [安装与使用](#安装与使用)
  - [快速安装](#快速安装)
  - [快速使用](#快速使用)

---

## **✨ NeoAI 的功能**

NeoAI 是一款创新的工具，能够帮助您通过自然语言控制电脑，实现远程操作、自动化任务和设备管理。它功能强大且简单易用，支持以下场景：

| 设备     | 示例对话                                                                                               | 功能展示            |
| -------- | ------------------------------------------------------------------------------------------------------ | ------------------- |
| **电脑** | **"我的工作报表文件在哪？"** <br> **"您的工作报表文件位于 D 盘的 Project 文件夹，需要我帮您打开吗？"** | ![PC](images/PC.png)       |
| **手机** | **"10 分钟后帮我重启电脑。"** <br> **"好的，已为您添加定时执行。"**                                    | ![Phone](images/Phone.jpg) |

## NeoAI 支持通过任何带有浏览器的设备操作。您可以在您的主机上创建服务，再在手机上对 AI 输入想要执行的操作，AI 会帮您立刻执行。

## **安装与使用**

### **快速安装**

1. **克隆仓库**

   ```bash
   git clone https://github.com/TheD0ubleC/NeoAI.git
   ```

2. **进入目录**

   ```bash
   cd NeoAI
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **启动 NeoAI**

   - **WebUI 模式：**

     ```bash
     python ./src/web-ui.py
     ```

   - **终端模式：**
     ```bash
     python ./src/main.py
     ```

---

### **快速使用**

#### **WebUI 模式**

1. 启动后打开浏览器，访问：

   ```
   localhost:7820
   ```

2. 点击左上角的 **NeoAI** > ⚙️ **设置** 进行初次配置。
   或直接访问：
   ```
   localhost:7820/config
   ```

#### **终端模式**

1. 启动程序，若正确显示 NeoAI 的 LOGO：

   ```
   +=========================================+
    ███╗   ██╗███████╗ ██████╗      █████╗ ██╗
    ████╗  ██║██╔════╝██╔═══██╗    ██╔══██╗██║
    ██╔██╗ ██║█████╗  ██║   ██║    ███████║██║
    ██║╚██╗██║██╔══╝  ██║   ██║    ██╔══██║██║
    ██║ ╚████║███████╗╚██████╔╝    ██║  ██║██║
     ╚═╝  ╚═══╝╚══════╝ ╚═════╝     ╚═╝  ╚═╝╚═╝
   +=========================================+
   ```

2. 输入以下命令查看帮助并完成初次配置：

   ```bash
   .help
   ```

3. 按需设置完成后，开始享受 AI 的强大功能！

---

### **NeoAI 的亮点功能**

- **远程操作设备：**

  - 随时随地通过手机或其他设备远程控制电脑。

- **快速文件管理：**

  - 通过简单的对话找到文件并直接打开。

- **自动化任务：**

  - 定时重启、定时关机，轻松安排任务。

- **设备管理：**
  - 监控和控制多个设备，高效便捷。

---

**快来尝试 NeoAI！**

![Star Trend](https://starchart.cc/thed0ublec/neoai.svg)
