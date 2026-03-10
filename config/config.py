import os
import shutil
import json
import sys
import tkinter as tk
from tkinter import messagebox


APP_NAME = "Azulyn_Prayer"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)
USER_KEYBINDS = os.path.join(APPDATA_DIR, "keybinds.json")
USER_CONFIG = os.path.join(APPDATA_DIR, "config.json")

# PyInstaller-safe way to locate bundled files
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_KEYBINDS_IN_APP = os.path.join(BASE_DIR, "config", "keybinds.json")
DEFAULT_CONFIG_IN_APP = os.path.join(BASE_DIR, "config", "config.json")
DEFAULT_KEYBINDS = os.path.join(BASE_DIR, "", "keybinds.json")
DEFAULT_CONFIG = os.path.join(BASE_DIR, "", "config.json")

if not os.path.exists(USER_KEYBINDS):
    if os.path.exists(DEFAULT_KEYBINDS_IN_APP):
        shutil.copy(DEFAULT_KEYBINDS_IN_APP, USER_KEYBINDS)
    else:
        if os.path.exists(DEFAULT_KEYBINDS):
            shutil.copy(DEFAULT_KEYBINDS, USER_KEYBINDS)
        else:
            print("file not found at ", DEFAULT_KEYBINDS_IN_APP)
            raise FileNotFoundError("Default keybinds.json not found in bundled resources.")

if not os.path.exists(USER_CONFIG):
    if os.path.exists(DEFAULT_CONFIG_IN_APP):
        shutil.copy(DEFAULT_CONFIG_IN_APP, USER_CONFIG)
    else:
        if os.path.exists(DEFAULT_CONFIG):
            shutil.copy(DEFAULT_CONFIG, USER_CONFIG)
        else:
            print("file not found at ", DEFAULT_CONFIG_IN_APP)
            raise FileNotFoundError("Default config.json not found in bundled resources.")

def show_error_popup(message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Error", message)
    root.destroy()  # Destroy the root window after the popup

try:
    with open(USER_KEYBINDS, "r", encoding="utf-8") as f:
        keybind_config = json.load(f)
except json.JSONDecodeError as e:
    error_message = (
        f"Error: Your .JSON file is not formatted correctly.\n"
        f"Fix it at: '{USER_KEYBINDS}'\n"
        f"Line {e.lineno}, Column {e.colno}.\n"
        f"Message: {e.msg}"
    )
    show_error_popup(error_message)
    sys.exit(1)
except FileNotFoundError:
    error_message = f"Error: The file '{USER_KEYBINDS}' was not found."
    show_error_popup(error_message)
    sys.exit(1)

# Ensure "PRAYER_KEYBINDS" exists in user_keybinds
keybind_config["PRAYER_KEYBINDS"] = keybind_config.get("PRAYER_KEYBINDS", {})

try:
    with open(USER_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
except json.JSONDecodeError as e:
    error_message = (
        f"Error: Your .JSON file is not formatted correctly.\n"
        f"Fix it at: '{USER_CONFIG}'\n"
        f"Line {e.lineno}, Column {e.colno}.\n"
        f"Message: {e.msg}"
    )
    show_error_popup(error_message)
    sys.exit(1)
except FileNotFoundError:
    error_message = f"Error: The file '{USER_CONFIG}' was not found."
    show_error_popup(error_message)
    sys.exit(1)

