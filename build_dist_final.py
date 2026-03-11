import os
import shutil
import subprocess
from pathlib import Path

# ==== CONFIGURATION ====
PYTHON_SCRIPTS = [
    "main.py",
    #"pray_detector2.py",
    "setup.py",
    #"config/config.py",
]

RESOURCE_FILES = [
    "config/keybinds.json",
    "config/config.json",
]

RESOURCE_DIRS = [
    "resources",
]

DIST_DIR = Path("dist_final")

# ==== CLEAN UP ====
print("[✓] Cleaning previous build...")
shutil.rmtree(DIST_DIR, ignore_errors=True)
DIST_DIR.mkdir(exist_ok=True)

for script_path in PYTHON_SCRIPTS:
    print(f"[✓] Building {script_path}...")

    icon_path = "resources/azulyn_icon_reflect.ico"
    rel_path = Path(script_path).with_suffix(".exe")            # e.g. Scripts/RS_Trainer.exe
    output_path = DIST_DIR / rel_path.parent                    # e.g. dist_final/Scripts

    output_path.mkdir(parents=True, exist_ok=True)

    add_data_flags = ' '.join([
        f'--add-data "{file};{Path(file).parent}"' for file in RESOURCE_FILES
    ])

    cmd = (
        f'python -m PyInstaller '
        f'--onefile '
        f'--noconsole '
        f'--icon="{icon_path}" '
        f'--collect-all cv2 '
        f'--collect-all numpy '
        f'--collect-all pynput '
        f'--collect-all mss '
        f'--collect-all scikit-image '
        f'{add_data_flags} '
        f'--distpath "{output_path}" '
        f'"{script_path}"'
    )
    subprocess.run(cmd, shell=True, check=True)

    # Determine source .exe and destination
    exe_name = Path(script_path).stem + ".exe"
    built_exe = Path("dist") / exe_name
    rel_target_path = Path(script_path).with_suffix(".exe")  # Scripts/RS_Trainer.exe
    final_exe_path = DIST_DIR / rel_target_path

    if built_exe.exists():
        print(f"[✓] Copying {exe_name} to dist_final/{rel_target_path.parent}...")
        final_exe_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(built_exe, final_exe_path)


# ==== COPY RESOURCE FILES (preserve structure) ====
for file in RESOURCE_FILES:
    src_file = Path(file)
    if src_file.exists():
        target_path = DIST_DIR / src_file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_file, target_path)
        print(f"[✓] Copied {src_file} → {target_path}")


# ==== COPY RESOURCE DIRECTORIES ====
for dir_name in RESOURCE_DIRS:
    src_dir = Path(dir_name)
    dst_dir = DIST_DIR / dir_name
    if src_dir.exists():
        print(f"[✓] Copying {dir_name}/ to final dist...")
        shutil.copytree(src_dir, dst_dir)

# ==== CLEAN BUILD TRASH ====
print("[✓] Cleaning PyInstaller temp files...")
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)
shutil.rmtree("__pycache__", ignore_errors=True)
for spec in Path().glob("*.spec"):
    spec.unlink()

print(f"\n✅ Done! Final dist ready at: {DIST_DIR.resolve()}")
