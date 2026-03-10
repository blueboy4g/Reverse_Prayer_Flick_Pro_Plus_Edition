import keyboard
import win32con
import win32gui
from pray_detector import *
from tkinter import filedialog
from tkinter import ttk
import subprocess
import threading
import requests
import webbrowser
from config.config import *
import setup

block_counter = 0
block_type = ""
HOTKEY_TO_PRAYER = {}  # will populate from keybinds

import keyboard
import threading
import time

block_counter = 0
block_type = ""

# Find the initial region for prayer detection
region = find_scaled_image()

# Modifier key mapping
MODIFIER_TO_HOTKEY = {
    "LCTRL": "ctrl",
    "LSHIFT": "shift",
    "LALT": "alt",
    "CTRL": "ctrl",
    "SHIFT": "shift",
    "ALT": "alt"
}

# Build hotkey → prayer mapping from keybinds
HOTKEY_TO_PRAYER = {}
for ability, keys in keybind_config["PRAYER_KEYBINDS"].items():
    hotkey_parts = []
    for k in keys:
        k_upper = k.upper()
        if k_upper in MODIFIER_TO_HOTKEY:
            hotkey_parts.append(MODIFIER_TO_HOTKEY[k_upper])
        else:
            hotkey_parts.append(k.lower())
    hotkey = "+".join(hotkey_parts)
    HOTKEY_TO_PRAYER[hotkey] = ability.lower()
    print("Registering hotkey:", hotkey)

# ---------------- Thread: Update current active prayer ----------------
def monitor_prayer():
    """Continuously updates block_type with the current active prayer."""
    global block_type
    while True:
        current_prayer = is_praying(region)
        if current_prayer:
            block_type = current_prayer
        else:
            block_type = ""
        time.sleep(0.05)  # ~20 FPS

threading.Thread(target=monitor_prayer, daemon=True).start()

# ---------------- Hotkey blocking logic ----------------
def on_hotkey_pressed(hotkey):
    """
    Blocks a key press ONLY if the hotkey corresponds to
    the currently active prayer (prevent re-activating same prayer).
    """
    global block_counter
    requested_prayer = HOTKEY_TO_PRAYER.get(hotkey)

    # If the requested prayer is the same as current active prayer, block it
    if requested_prayer and requested_prayer == block_type:
        block_counter += 1
        print(f"Blocked key press for {block_type} prayer")
        return True  # suppress key
    # Otherwise allow it (switching prayers or toggling off)
    return False

# ---------------- Register hotkeys ----------------
for hotkey in HOTKEY_TO_PRAYER:
    keyboard.add_hotkey(
        hotkey,
        lambda h=hotkey: on_hotkey_pressed(h),
        suppress=True
    )

# ---------------- Optional: monitor block counter ----------------
def print_block_count():
    """Just prints how many blocks happened (for debug)."""
    global block_counter
    while True:
        print(f"Blocked Inputs: {block_counter}, Active Prayer: {block_type}")
        time.sleep(2)

# Uncomment to see debug info in console
threading.Thread(target=print_block_count, daemon=True).start()

keyboard.wait()  # Keep script running


def make_window_always_on_top():
    hwnd = win32gui.GetForegroundWindow()  # Get current foreground window
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# ----------------- Config -----------------
CURRENT_VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/blueboy4g/Reverse_Player_Flick_Pro_Plus_Edition/main/version.json"

APP_NAME = "Azulyn_Prayer"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)

KEYBINDS_FILE = os.path.join(APPDATA_DIR, "keybinds.json")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")
from pathlib import Path

ICON_PATH = "Resources/azulyn_icon.ico"
# ------------------------------------------

with open("config/keybinds.json", "r", encoding="utf-8") as f:
    print("Loading default keybinds from: ", "config/keybinds.json")
    default_keybinds = json.load(f)

# Check for missing keys under "PRAYER_KEYBINDS"
missing_keybinds = {key: value for key, value in default_keybinds["PRAYER_KEYBINDS"].items() if key not in keybind_config["PRAYER_KEYBINDS"]}

if missing_keybinds:
    # Add missing keys to "PRAYER_KEYBINDS"
    keybind_config["PRAYER_KEYBINDS"].update(missing_keybinds)

    # Save the updated user keybinds without reformatting other entries
    with open(USER_KEYBINDS, "w", encoding="utf-8") as f:
        json.dump(keybind_config, f, indent=4, separators=(',', ': '))
    print(f"Added missing keybinds under 'PRAYER_KEYBINDS': {missing_keybinds}")
else:
    print("All keybinds under 'PRAYER_KEYBINDS' are already present.")

def check_for_update():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        data = response.json()
        latest_version = data["version"]
        download_url = data["download_url"]
        notes = data.get("notes", "")
        if latest_version != CURRENT_VERSION:
            if messagebox.askyesno("Update Available", f"New version {latest_version} available:\n\n{notes}\n\nDownload now?"):
                webbrowser.open(download_url)
        else:
            messagebox.showinfo("No Update", f"You're running the latest version ({CURRENT_VERSION})")
    except Exception as e:
        messagebox.showerror("Update Check Failed", str(e))

def start_script(exe_path, log_output=False, args=None):
    full_path = os.path.abspath(exe_path)
    args = args or []
    def run():
        try:
            process = subprocess.Popen(
                [full_path] + args,
                cwd=os.path.dirname(full_path),
                stdout=subprocess.PIPE if log_output else None,
                stderr=subprocess.STDOUT if log_output else None,
                text=True
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {exe_path}:\n{e}")
    threading.Thread(target=run).start()

def open_file_editor(filepath):
    if not os.path.isfile(filepath):
        messagebox.showerror("Error", f"File not found: {filepath}")
        return
    subprocess.Popen([get_default_editor(), filepath])

def get_default_editor():
    return os.environ.get("EDITOR", "notepad")

def open_donation():
    webbrowser.open("https://buymeacoffee.com/azulyn")

def open_discord():
    webbrowser.open("https://discord.gg/uhnJpVKXpu")

def open_rotation():
    webbrowser.open("https://blueboy4g.github.io/RS_Rotation_Creator/")

def open_youtube():
    webbrowser.open("https://www.youtube.com/@Azulyn1")

# --------------- UI Setup ----------------
root = tk.Tk()
root.title("Pray Flick Pro")
#TODO config
root.geometry("460x100")
root.iconbitmap(ICON_PATH)
#TODO config
# make_window_always_on_top()

# Dark button styling
style = ttk.Style()
style.theme_use("default")
style.configure("Dark.TButton", foreground="white", background="#444", padding=6)
style.map("Dark.TButton", background=[("active", "#555")])

key_bind_config = tk.StringVar(value=KEYBINDS_FILE)
config_file = tk.StringVar(value=CONFIG_FILE)


ascii_title = r"""
   _____               .__                
  /  _  \ __________ __|  | ___.__. ____  
 /  /_\  \\___   /  |  \  |<   |  |/    \ 
/    |    \/    /|  |  /  |_\___  |   |  \
\____|__  /_____ \____/|____/ ____|___|  /
        \/      \/          \/         \/ 
"""

# Layout Frames
top_frame = tk.Frame(root)
top_frame.pack(pady=5, fill="x")

left = tk.Frame(top_frame)
right = tk.Frame(top_frame)
left.pack(side="left", padx=5, expand=True, fill="both")
right.pack(side="right", padx=5, expand=True, fill="both")

log_frame = tk.Frame(root)
log_frame.pack(pady=0, fill="both")

bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=(5, 0))

footer = tk.Frame(root)
footer.pack(side="right", pady=(10, 0))
block_counter_var = tk.StringVar(value="Blocks: 0")
tk.Label(
    footer,
    textvariable=block_counter_var,
    font=("Courier", 8)
).pack(side="left", padx=5, pady=0)

block_type_var = tk.StringVar(value="")
tk.Label(
    footer,
    textvariable=block_type_var,
    font=("Courier", 8)
).pack(side="left", padx=5, pady=0)

def update_block_counter():
    # block_counter_var.set(f"Blocks: {block_counter}")
    block_counter_var.set(f"Blocked Inputs: {block_counter}")
    block_type_var.set(f"Active Prayer: {block_type}")
    root.after(100, update_block_counter)  # refresh every 100ms

ttk.Button(left, text="Setup Pray Pro", style="Gray.TButton",
           #TODO command=lambda: start_script("key_binds.exe")).pack(pady=2, fill="x")
           #TODO this will work once it goes into exe for now the mod keys dont show??
           command=lambda: setup.start_setup(KEYBINDS_FILE)).pack(pady=2, fill="x")

ttk.Button(right, text="Edit Config", style="Gray.TButton",
           command=lambda: open_file_editor(config_file.get())).pack(pady=2, fill="x")


ttk.Button(bottom_frame, text="Check for Updates", style="Gray.TButton",
           command=check_for_update).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Youtube", style="Gray.TButton",
           command=open_youtube).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Discord", style="Gray.TButton",
           command=open_discord).pack(side="left", padx=5, pady=1)
ttk.Button(bottom_frame, text="Donate", style="Gray.TButton",
           command=open_donation).pack(side="left", padx=5, pady=1)


tk.Label(footer, font=("Courier", 8), text=f"Current Version: {CURRENT_VERSION}").pack(side="right", padx=5, pady=0)
update_block_counter()
root.mainloop()