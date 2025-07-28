import os
import shutil

def classify_files(folder_path):
    if not os.path.exists(folder_path):
        return "Folder not found."

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            ext = filename.split('.')[-1].lower()
            target_dir = os.path.join(folder_path, ext + "_files")

            os.makedirs(target_dir, exist_ok=True)

            try:
                shutil.move(file_path, os.path.join(target_dir, filename))
            except Exception as e:
                print(f"Failed to move {filename}: {e}")
    return "Classification complete."