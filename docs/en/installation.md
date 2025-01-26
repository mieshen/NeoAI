# Installation/Deployment

---

## 1. Retrieve the Project

### **_Clone_** the project or **_directly download_** the project

- #### Direct Download

Visit our repository [NeoAI](https://github.com/TheD0ubleC/NeoAI)

![alt text](images/github-main-image.png)

- 1. Click `Code`
- 2. Click `Download ZIP`

---

- #### Clone the Project

```bash
git clone https://github.com/TheD0ubleC/NeoAI.git
```

#### If **_cloning is successful_**, you will see output similar to the following:

```text
Cloning into 'NeoAI'...
remote: Enumerating objects: XX, done.
remote: Counting objects: 100% (XX/XX), done.
remote: Compressing objects: 100% (XX/XX), done.
remote: Total XX (delta XX), reused XX (delta XX), pack-reused XX
Receiving objects: 100% (XX/XX), XX MiB | XX KiB/s, done.
Resolving deltas: 100% (XX/XX), done.
```

> Here, `XX` represents numbers or the count of files, while `MiB` and `KiB/s` indicate download speed and size. Seeing **"done"** confirms successful cloning.

#### After cloning successfully, proceed directly to [Start Deployment](#start-deployment).

#### If **_cloning fails_**, you will see output similar to the following:

---

### Common Issues and Solutions

#### Network Connection Issues

```text
fatal: unable to access 'https://github.com/TheD0ubleC/NeoAI.git': Could not resolve host: github.com
```

**Solution**:

- If you are located in mainland China, use a VPN or other tools to access GitHub.
- Check your DNS settings to ensure `github.com` can be correctly resolved.

---

#### Permission Issues

```text
fatal: repository 'https://github.com/TheD0ubleC/NeoAI.git/' not found
```

**Solution**:

- Ensure the repository URL is correct. If it’s a private repository, verify your access permissions.
- If cloning via HTTPS, ensure the correct username and password for your GitHub account are configured.
- Using SSH for cloning is recommended:

  1. Add an SSH key to GitHub.
  2. Clone the repository using the following command:

  ```bash
  git clone git@github.com:TheD0ubleC/NeoAI.git
  ```

---

#### Insufficient Storage Space

```text
fatal: unable to create file 'filename': No space left on device
```

**Solution**:

- Check your local disk space to ensure sufficient storage space for cloning the repository.
- Free up space by cleaning temporary or unnecessary files on your disk.

---

#### Proxy Settings Issues

```text
fatal: unable to access 'https://github.com/TheD0ubleC/NeoAI.git': The requested URL returned error: 403
```

**Solution**:

- If using a proxy, verify the proxy settings are correct, or temporarily disable the proxy and try again.
- Reset Git proxy settings using the following commands:

  ```bash
  git config --global --unset http.proxy
  git config --global --unset https.proxy
  ```

---

## 2. Start Deployment

### Navigate to the Project Directory

```bash
cd NeoAI
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Choose a Running Mode

### WebUI

- **Advantages**:
  - Provides a graphical user interface, making operations simple.
  - Supports remote access.
  - Easy to configure and user-friendly.

#### Start Command:

```bash
python src/web-ui.py
```

---

### Terminal

- **Advantages**:
  - Suitable for environments without a desktop.
  - Consumes fewer resources.

#### Start Command:

```bash
python src/main.py
```

---

## Next, we will begin configuring NeoAI. Let’s proceed to

# [>Configuration Tutorial](/en/tutorial.md)
