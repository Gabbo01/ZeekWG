<div align="center">

# Zeek Web GUI Analyzer

**🔍 The first Zeek Web GUI with built-in AI to analyze your PCAP files!**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![GitHub release (latest by date)](https://img.shields.io/badge/release-v1.0-blue)](https://github.com/Gabbo01/ZeekWG/releases)
[![Linkedin](https://img.shields.io/badge/Linked-in-blue)](https://www.linkedin.com/in/gabriele-bencivenga-93797b147/)

<img src="images/dash1.png" alt="Zeek Web GUI Screenshot" style="border-radius:8px; margin-top:20px"/>

</div>

---

## 📚 Table of Contents

- [🚀 Features](#-features)  
- [🔧 Requirements](#-requirements)  
- [📦 Python Dependencies](#-python-dependencies)  
- [🔑 Gemini API Key](#-gemini-api-key)  
- [🚀 Usage](#-usage)  
- [💡 Examples](#-examples)  
- [📁 Project Structure](#-project-structure)  
- [🤝 Contributing](#-contributing)  
- [📜 License](#-license)

---

## 🚀 Features

- 📁 **PCAP/PCAPNG Upload**  
  Easily upload `.pcap` or `.pcapng` files through the web interface.

- ⚙️ **Automatic Log Generation with [Zeek](https://docs.zeek.org/en/master/about.html)**  
  Uploaded files are processed using Zeek, generating 20+ types of logs.

- 🔍 **Log Filtering Interface**  
  Browse and filter logs through the GUI to focus on relevant network activity.

- 🤖 **AI-Powered Analysis**  
  Analyze logs with an integrated LLM (powered by Gemini API) for contextual insights.

- 🎯 **Filtered Log Analysis**  
  Send only filtered logs to the AI to optimize performance and precision.


---

## 🔑 Gemini API Key

To enable the AI analysis feature:

1. Get your key from [Google Gemini API](https://ai.google.dev/gemini-api/docs/quickstart)
2. Put it in /app/app.py file

<img src="images/googleapikey.png" alt="Set Google API Key" width="600"/>

---
## 🚀 Usage

1.  **Clone the repository**

    ```bash
    git clone https://github.com/Gabbo01/ZeekWG
    cd ZeekWG
    ```

2.  **Build and start services with Docker Compose**

    Ensure you have **Docker** and **Docker Compose** installed on your system.

    ```bash
    docker compose build
    docker compose up -d 
    ```

    The `docker compose build` command will create the necessary Docker images (or rebuild them if there have been changes). Subsequently, `docker compose up -d` will start the Flask server and any other services defined in your `docker-compose.yml` file in the background.

3.  **Open your browser**

    ```
    http://localhost:5000
    ```

4.  **Upload your `.pcap` / `.pcapng` file**
    Logs will be generated automatically.

5.  **Filter logs and run AI analysis as needed**
---

## 💡 Examples

### ✅ Example 1: Full Log Analysis with AI

1. Upload a `.pcap` file  
2. Click **"Analizza tutti i log"**  
3. The AI provides a complete security overview

<img src="images/AIanalysis.png" alt="AI Analysis Example" width="700"/>

---

### 🔬 Example 2: Focused Log Analysis

1. Upload a `.pcap` file  
2. Open `conn.log`  
3. Apply a filter with **"Applica filtri"** and analyze truncated data

<img src="images/dash2.png" alt="Filtered Analysis" width="700"/>

---

## 📁 Project Structure

```
app/
├── app.py                 # Main Python Flask application
├── templates/             # HTML templates
├── uploads/               # Uploaded PCAPs
├── zeek_logs/             # Zeek-generated logs

```

---

## 🤝 Contributing

Contributions are welcome!  
Open an issue or submit a PR for bugs, improvements, or ideas 💡

---

## 📜 License

Licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0).  
See the `LICENSE` file for more details.
