# NeoAI: No Coding Required! Let AI Take Control of Your Computer! | NeoAI：无需一行代码！让 AI 掌控您的电脑！

## [简体中文文档点我](docs/README(zh-CN).md)

<p align="center">
  <img src="docs/LOGO.png" alt="Logo" width="400" />
</p>

<section align="center">
  <img src="https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge" alt="Windows Support">
  <img src="https://img.shields.io/badge/platform-macOS-lightgreen?style=for-the-badge" alt="macOS Support">
  <img src="https://img.shields.io/badge/platform-Linux-green?style=for-the-badge" alt="Linux Support">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License">
</section>

---

**Introduction:** NeoAI is currently in the testing phase and may have some unknown issues.

If you are willing, you can become a contributor to NeoAI and help us improve it together!

---

## **Table of Contents**

- [Features of NeoAI](#features-of-neoai)
- [Installation and Usage](#installation-and-usage)
  - [Quick Installation](#quick-installation)
  - [Quick Start](#quick-start)

---

## **✨ Features of NeoAI**

NeoAI is an innovative tool that enables you to control your computer through natural language, facilitating remote operations, task automation, and device management. It is powerful yet easy to use and supports the following scenarios:

| Device  | Example Dialog                                                             | Feature Demonstration     |
|---------|----------------------------------------------------------------------------|---------------------------|
| **PC**  | **"Where is my work report file?"**  <br> **"Your work report file is located in the Project folder on drive D. Shall I open it for you?"** | ![PC](docs/PC.png)        |
| **Phone** | **"Restart the computer in 10 minutes."** <br> **"Sure, I have scheduled it for you."**                 | ![Phone](docs/Phone.jpg) |

NeoAI supports operation from any device with a browser. You can host the service on your machine and then input commands to the AI via your phone, and it will execute them immediately.

---

## **Installation and Usage**

### **Quick Installation**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/TheD0ubleC/NeoAI.git
   ```

2. **Navigate to the Directory**
   ```bash
   cd NeoAI
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start NeoAI**

   - **WebUI Mode:**
     ```bash
     python ./src/web-ui.py
     ```

   - **Terminal Mode:**
     ```bash
     python ./src/main.py
     ```

---

### **Quick Start**

#### **WebUI Mode**

1. After starting, open your browser and visit:
   ```
   localhost:7820
   ```

2. Click **NeoAI** > ⚙️ **Settings** in the top left corner to perform initial configuration.
   Or directly visit:
   ```
   localhost:7820/config
   ```

#### **Terminal Mode**

1. Start the program. If NeoAI’s logo displays correctly:
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

2. Enter the following command to view help and complete the initial configuration:
   ```bash
   .help
   ```

3. After setup, start enjoying the powerful features of NeoAI!

---

### **Highlight Features of NeoAI**

- **Remote Device Operations:**
  - Control your computer remotely from your phone or other devices, anytime, anywhere.

- **Quick File Management:**
  - Find and open files with simple conversations.

- **Task Automation:**
  - Schedule tasks like restarting or shutting down with ease.

- **Device Management:**
  - Monitor and manage multiple devices efficiently.

---

**Try NeoAI Now!**

![Star Trend](https://starchart.cc/thed0ublec/neoai.svg)

