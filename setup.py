import json
import os
from tkinter import messagebox
import tkinter as tk
from tkinter import messagebox
import json
import os

import win32con
import win32gui


APP_NAME = "Azulyn_Prayer"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
CONFIG_PATH = os.path.join(APPDATA_DIR, "keybinds.json")


ICON_PATH = "resources/azulyn_icon.ico"

MODIFIER_ALIASES = {
    "CTRL": "LCTRL", "LCTRL": "LCTRL",
    "SHIFT": "LSHIFT", "LSHIFT": "LSHIFT",
    "ALT": "LALT", "LALT": "LALT"
}

class Reverse_Prayer_Flick_Pro_Plus_Edition:
    def __init__(self, root, config_path=None):
        self.root = root
        self.root.title("Pray Flick Pro")
        self.prayers = {}
        self.config_path = config_path or CONFIG_PATH
        self.setup_ui()
        self.load_json()

    def setup_ui(self):
        # Scrollable area
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, height=150)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.rows_container = self.scrollable_frame  # use same frame for alignment

        # Bottom save button
        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.X, pady=10)

        tk.Button(bottom, text="SAVE", command=self.save_json, background='gray', foreground='black', fg='black', width=20,
                  font=('Helvetica 13 bold italic') ).pack()

    def add_section(self, title, prayer_list, start_row):
        collapsed = tk.BooleanVar(value=False)

        # Row: Section label in col 0, expand/collapse button in col 1
        tk.Label(self.rows_container, text="       " + title, font=("Arial", 12, "bold")).grid(
            row=start_row, column=0, sticky="w", padx=5
        )

        toggle_button = tk.Button(self.rows_container, text="[+]", width=3)
        toggle_button.grid(row=start_row, column=0, sticky="w")

        # Content frame (hidden until expanded)
        content_frame = tk.Frame(self.rows_container)
        content_frame.grid(row=start_row + 1, column=0, columnspan=5, sticky="w")
        #content_frame.grid_remove()

        def toggle():
            if collapsed.get():
                content_frame.grid()
                toggle_button.config(text="[-]")
                collapsed.set(False)
            else:
                content_frame.grid_remove()
                toggle_button.config(text="[+]")
                collapsed.set(True)

        toggle_button.config(command=toggle)

        # ➕ Header row inside each section
        tk.Label(content_frame, text="Prayer", width=18, anchor="w").grid(row=0, column=0, padx=5, sticky="w")
        tk.Label(content_frame, text="Key", width=12, anchor="w").grid(row=0, column=1, padx=5, sticky="w")
        tk.Label(content_frame, text="Ctrl", width=8, anchor="w").grid(row=0, column=2, padx=5)
        tk.Label(content_frame, text="Shift", width=8, anchor="w").grid(row=0, column=3, padx=5)
        tk.Label(content_frame, text="Alt", width=8, anchor="w").grid(row=0, column=4, padx=5)

        # prayer rows (start at row=1 now)
        for i, (name, keys) in enumerate(prayer_list, start=1):
            self.add_prayer_row(content_frame, i, name, keys)

        return start_row + 2 + len(prayer_list)


    def load_json(self):
        if not os.path.exists(CONFIG_PATH):
            messagebox.showerror("Missing File", f"Cannot find: {CONFIG_PATH}")
            return

        with open(self.config_path, "r") as f:
            data = json.load(f)

        keybinds = data.get("PRAYER_KEYBINDS", {})

        # Sort prayers by their appearance in the JSON
        prayers = list(keybinds.items())

        sections = {
            "Prayers": []
        }

        current_section = "Prayers"
        for name, keys in prayers:
            # if name.lower() == "adrenaline_potion":
            #     current_section = "Misc"
            # if name.lower() == "assault":
            #     current_section = "Melee"
            # if name.lower() == "binding_shot":
            #     current_section = "Range"
            # if name.lower() == "animate_dead":
            #     current_section = "Magic"
            # if name.lower() == "bloat":
            #     current_section = "Necromancy"
            # if name.lower() == "anticipation":
            #     current_section = "Defence"

            sections[current_section].append((name, keys))

        row = 1
        for section_name, prayer_list in sections.items():
            row = self.add_section(section_name, prayer_list, row)

    def save_json(self):
        data = {"PRAYER_KEYBINDS": {}}

        for name, (modifiers, key_entry) in self.prayers.items():
            key = key_entry.get().strip()
            mods = []
            if modifiers["ctrl"].get():
                mods.append("LCTRL")
            if modifiers["shift"].get():
                mods.append("SHIFT")
            if modifiers["alt"].get():
                mods.append("ALT")
            if key:
                mods.append(key.upper())
            data["PRAYER_KEYBINDS"][name] = mods
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo("Saved", f"Saved to:\n{CONFIG_PATH}")

    def add_prayer_row(self, parent_frame, row_num, prayer_name, keys):
        tk.Label(parent_frame, text=prayer_name, width=25, anchor="w").grid(row=row_num, column=0, padx=5, sticky="w")

        key_entry = tk.Entry(parent_frame, width=12)
        key_entry.grid(row=row_num, column=1, padx=5, sticky="w")

        ctrl_var = tk.BooleanVar()
        shift_var = tk.BooleanVar()
        alt_var = tk.BooleanVar()

        tk.Checkbutton(parent_frame, variable=ctrl_var).grid(row=row_num, column=2, padx=5)
        tk.Checkbutton(parent_frame, variable=shift_var).grid(row=row_num, column=3, padx=5)
        tk.Checkbutton(parent_frame, variable=alt_var).grid(row=row_num, column=4, padx=5)

        main_key = None

        for k in keys:
            normalized = MODIFIER_ALIASES.get(k.upper(), None)
            if normalized == "LCTRL":
                ctrl_var.set(True)
            elif normalized == "LSHIFT":
                shift_var.set(True)
            elif normalized == "LALT":
                alt_var.set(True)
            else:
                key_entry.insert(0, k.upper())

        self.prayers[prayer_name] = (
            {"ctrl": ctrl_var, "shift": shift_var, "alt": alt_var},
            key_entry
        )

def make_window_always_on_top():
    hwnd = win32gui.GetForegroundWindow()  # Get current foreground window
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

def start_setup(config_path=None):
    root = tk.Tk()
    root.iconbitmap(ICON_PATH)
    #TODO use the config
    #make_window_always_on_top()
    #TODO use the config
    root.geometry("500x230")
    app = Reverse_Prayer_Flick_Pro_Plus_Edition(root)
    root.mainloop()

if __name__ == "__main__":
    start_setup()