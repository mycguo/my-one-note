import sys
import os
from pathlib import Path

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app import load_notebooks, save_notebooks, NOTEBOOKS_FILE
from utils.encryption import is_encryption_enabled

def migrate():
    print("Checking encryption status...")
    if not is_encryption_enabled():
        print("❌ Encryption is NOT enabled. Check secrets.toml.")
        return

    print("✅ Encryption is enabled.")
    
    print(f"Loading notebooks from {NOTEBOOKS_FILE}...")
    # This will load plain text (fallback) or encrypted (if already encrypted)
    notebooks = load_notebooks()
    print(f"Loaded {len(notebooks)} notebooks.")
    
    print("Saving notebooks (should be encrypted now)...")
    save_notebooks(notebooks)
    
    # Verify
    print("Verifying file content...")
    with open(NOTEBOOKS_FILE, 'rb') as f:
        content = f.read()
        try:
            content.decode('utf-8')
            # If it decodes as utf-8 and starts with {, it's likely plain text
            if content.strip().startswith(b'{'):
                print("❌ File still appears to be plain text JSON!")
            else:
                print("✅ File content is binary/encrypted (or at least not plain JSON).")
        except UnicodeDecodeError:
            print("✅ File content is binary/encrypted (not valid UTF-8).")

if __name__ == "__main__":
    migrate()
