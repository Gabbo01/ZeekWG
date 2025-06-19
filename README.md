# Zeek Web GUI Analyzer

**The first Zeek Web GUI with built-in AI to analyze your PCAP files!**

![dash1](images/dash1.png)

## 🚀 Features

1. **PCAP/PCAPNG Upload**  
   Easily upload `.pcap` or `.pcapng` files through the web interface.

2. **Automatic Log Generation with Zeek**  
   Uploaded files are processed using Zeek, generating 20+ types of logs for in-depth analysis.

3. **Log Filtering Interface**  
   Browse and filter logs conveniently through the GUI to focus on relevant network activity.

4. **AI-Powered Analysis**  
   Analyze the entire set of logs with an integrated LLM (currently powered by Gemini API) for contextual and intelligent insights.

5. **Filtered/Truncated Log Analysis**  
   Optimize resources by sending only filtered logs to the AI for targeted analysis.

---

## 🔧 Requirements

- **Python**: 3.11 or higher  
- **Zeek** and **zeek-cut** binaries installed at:  
  `/usr/local/zeek/bin/`  
  *(Update the code if your binaries are located elsewhere)*

---

## 📦 Python Dependencies

Make sure to install the following Python modules:

- `os`  
- `subprocess`  
- `flask`  
- `werkzeug`  
- `google-genai`  
- `markdown`  
- `datetime`

You can install the required external modules using:

```bash
pip install flask werkzeug google-genai markdown

### Google API Key for Gemini use

