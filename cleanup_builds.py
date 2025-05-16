import os
import shutil

def delete_folder(folder_name):
    if os.path.exists(folder_name) and os.path.isdir(folder_name):
        print(f"🗑️ Deleting folder: {folder_name}")
        shutil.rmtree(folder_name)
    else:
        print(f"❌ Folder not found: {folder_name}")

def delete_spec_files():
    for file in os.listdir():
        if file.endswith(".spec"):
            try:
                os.remove(file)
                print(f"🗑️ Deleted spec file: {file}")
            except Exception as e:
                print(f"❌ Failed to delete {file}: {e}")

def delete_exe_in_dist():
    dist_path = os.path.join(os.getcwd(), "dist")
    if os.path.exists(dist_path):
        for root, dirs, files in os.walk(dist_path):
            for file in files:
                if file.endswith(".exe"):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"🗑️ Deleted .exe: {file_path}")
                    except Exception as e:
                        print(f"❌ Failed to delete {file_path}: {e}")
    else:
        print("❌ 'dist' folder does not exist.")

def cleanup_pyinstaller_artifacts():
    print("🚮 Cleaning up PyInstaller build artifacts...\n")
    delete_folder("build")
    delete_spec_files()
    delete_exe_in_dist()
    print("\n✅ Cleanup completed!")

if __name__ == "__main__":
    cleanup_pyinstaller_artifacts()
