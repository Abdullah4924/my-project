import os
import shutil
import subprocess
import re
from datetime import datetime
from pathlib import Path

# Get Desktop path dynamically (no profile issues)
desktop = Path.home() / "Desktop"

# Set your folders (ON Desktop)
source_folder = str(desktop / "test")
destination_folder = str(desktop / "test2")

winrar_path = r"C:\Program Files\WinRAR\WinRAR.exe"  # Update if needed

# Extensions of archive files
archive_exts = ('.zip', '.rar', '.gz')

# Make sure destination exists
os.makedirs(destination_folder, exist_ok=True)

# Track already extracted archives
processed_archives = set()

# Function to extract directly into folder (and delete if from destination)
def extract_archive(archive_path, extract_to):
    print(f"📦 Extracting: {archive_path}")
    command = f'"{winrar_path}" x -ibck -o+ -inul -y "{archive_path}" "{extract_to}\\"'
    subprocess.run(command, shell=True)
    processed_archives.add(os.path.abspath(archive_path))

    # Delete archive only if it's inside the destination folder
    if archive_path.startswith(os.path.abspath(destination_folder)):
        try:
            os.remove(archive_path)
            print(f"🗑️ Deleted archive from destination: {archive_path}")
        except Exception as e:
            print(f"⚠️ Could not delete archive: {archive_path} → {e}")

# ✅ Step 1: Extract all archive files from source to destination
for filename in os.listdir(source_folder):
    file_path = os.path.join(source_folder, filename)
    if filename.lower().endswith(archive_exts):
        extract_archive(file_path, destination_folder)
    else:
        # ✅ Also copy non-archive files from source to destination (overwrite)
        dest_path = os.path.join(destination_folder, filename)
        try:
            shutil.copy2(file_path, dest_path)
            print(f"📁 Copied file: {filename}")
        except Exception as e:
            print(f"⚠️ Could not copy file {filename}: {e}")

# ✅ Step 2: Recursively extract archives inside destination
archives_found = True
while archives_found:
    archives_found = False
    for root, dirs, files in os.walk(destination_folder):
        for file in files:
            if file.lower().endswith(archive_exts):
                archive_path = os.path.abspath(os.path.join(root, file))
                if archive_path not in processed_archives:
                    extract_archive(archive_path, root)
                    archives_found = True

# ✅ Step 3: Move all non-archive files from subfolders to root (overwrite)
for root, dirs, files in os.walk(destination_folder):
    for file in files:
        full_path = os.path.join(root, file)
        if root != destination_folder and not file.lower().endswith(archive_exts):
            dest_path = os.path.join(destination_folder, file)
            try:
                if os.path.exists(dest_path):
                    os.remove(dest_path)  # Overwrite existing file
                shutil.move(full_path, dest_path)
                print(f"📁 Moved: {file} → {destination_folder}")
            except Exception as e:
                print(f"⚠️ Error moving {file}: {e}")
                
# ✅ Step 4: Delete all folders inside the destination folder
for item in os.listdir(destination_folder):
    item_path = os.path.join(destination_folder, item)
    if os.path.isdir(item_path):
        try:
            shutil.rmtree(item_path)
            print(f"🧹 Deleted folder: {item_path}")
        except Exception as e:
            print(f"⚠️ Could not delete folder {item_path}: {e}")

# ✅ Step 5 (fixed): Rename files that contain ddmmyy or ddmmyyyy tokens
from datetime import datetime
import os, re

today = datetime.now()
today_dd = today.strftime("%d")   # "01"
today_mm = today.strftime("%m")   # "09"
today_yyyy = today.strftime("%Y") # "2025"
today_yy = today.strftime("%y")   # "25"

# Regex: match ddmmyy or ddmmyyyy, not part of a bigger number
pattern = re.compile(
    r'(?<!\d)'                              # no digit before
    r'(?P<dd>0[1-9]|[12][0-9]|3[01])'       # day 01-31
    r'(?P<mm>0[1-9]|1[0-2])'                # month 01-12
    r'(?P<yy>\d{2}|\d{4})'                  # year (2 or 4 digits)
    r'(?!\d)'                               # no digit after
)

def is_valid_date(dd, mm, yy):
    """Validate if ddmmyy or ddmmyyyy is a real date."""
    try:
        if len(yy) == 2:  # ddmmyy format → assume 2000+
            datetime.strptime(dd + mm + yy, "%d%m%y")
        else:             # ddmmyyyy format
            datetime.strptime(dd + mm + yy, "%d%m%Y")
        return True
    except ValueError:
        return False

for filename in os.listdir(destination_folder):
    file_path = os.path.join(destination_folder, filename)
    if not os.path.isfile(file_path):
        continue

    m = pattern.search(filename)
    if not m:
        continue

    dd, mm, yy = m.group("dd"), m.group("mm"), m.group("yy")

    # Validate the date before renaming
    if not is_valid_date(dd, mm, yy):
        print(f"⏭️ Skipping {filename}: invalid date {dd}{mm}{yy}")
        continue

    # Preserve year format (2 or 4 digits)
    yy_part = today_yyyy if len(yy) == 4 else today_yy

    # Build replacement token (today’s dd+mm+yy)
    new_token = f"{today_dd}{today_mm}{yy_part}"

    # Replace only the first occurrence
    new_filename = filename[:m.start()] + new_token + filename[m.end():]

    if new_filename == filename:
        continue  # no change

    new_path = os.path.join(destination_folder, new_filename)

    # Prevent accidental overwrite
    if os.path.exists(new_path):
        print(f"⚠️ Skipping {filename}: target {new_filename} already exists")
        continue

    try:
        os.rename(file_path, new_path)
        print(f"✅ Renamed: {filename} → {new_filename}")
    except Exception as e:
        print(f"⚠️ Could not rename {filename}: {e}")


print("\n✅ All done! Archives flattened, Excel/.dat files copied, no folders created.")
#this is my second commit in code i want to know that is this going to work or not
