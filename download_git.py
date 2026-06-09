import os
import urllib.request
import zipfile

def download_and_extract():
    url = "https://github.com/git-for-windows/git/releases/download/v2.45.1.windows.1/MinGit-2.45.1-64-bit.zip"
    zip_path = "mingit.zip"
    extract_path = "mingit"
    
    print("Downloading MinGit from GitHub releases...")
    try:
        # Use urllib.request to download the zip file
        urllib.request.urlretrieve(url, zip_path)
        print("MinGit downloaded successfully.")
    except Exception as e:
        print(f"Failed to download MinGit: {e}")
        return False
        
    print("Extracting MinGit...")
    try:
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print("MinGit extracted successfully.")
    except Exception as e:
        print(f"Failed to extract MinGit: {e}")
        return False
        
    # Clean up the zip file
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    # Verify execution
    git_exe = os.path.join(extract_path, "cmd", "git.exe")
    if os.path.exists(git_exe):
        print(f"Verification successful: {git_exe} exists.")
        return True
    else:
        print("Verification failed: git.exe not found.")
        return False

if __name__ == "__main__":
    download_and_extract()
