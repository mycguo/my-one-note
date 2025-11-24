import json
import base64
import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configuration
DATA_DIR = Path("data")
NOTEBOOKS_FILE = DATA_DIR / "notebooks.json"

# Keys
OLD_KEY_STR = "0Im_YI3xVEbQqd6W2q7vqjulidabo3EW1nNHX_Y_N1E="
NEW_KEY_STR = "B1H0xgRBN7ERpLlOiqnJDf_h3FzuJuFQcaqdv4Y7zds="

def derive_user_key(user_id: str, master_key_str: str) -> bytes:
    """Derive user key from master key string"""
    try:
        master_key = base64.urlsafe_b64decode(master_key_str.encode())
    except:
        master_key = master_key_str.encode()
        
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=user_id.encode(),
        iterations=100000,
    )
    key_material = kdf.derive(master_key)
    return base64.urlsafe_b64encode(key_material)

def reencrypt():
    print("Starting re-encryption...")
    
    if not NOTEBOOKS_FILE.exists():
        print("No notebooks file found.")
        return

    # 1. Read and Decrypt with Old Key
    print("Reading and decrypting with OLD key...")
    try:
        with open(NOTEBOOKS_FILE, 'rb') as f:
            encrypted_data = f.read()
            
        old_user_key = derive_user_key("default_user", OLD_KEY_STR)
        f_old = Fernet(old_user_key)
        decrypted_data = f_old.decrypt(encrypted_data)
        json_data = json.loads(decrypted_data.decode('utf-8'))
        print("✅ Successfully decrypted with old key.")
    except Exception as e:
        print(f"❌ Failed to decrypt with old key: {e}")
        # Try reading as plain text just in case
        try:
            with open(NOTEBOOKS_FILE, 'r') as f:
                json_data = json.load(f)
            print("⚠️ File was plain text, proceeding to encrypt.")
        except:
            print("Fatal error: Could not read data.")
            return

    # 2. Encrypt with New Key
    print("Encrypting with NEW (global) key...")
    try:
        new_user_key = derive_user_key("default_user", NEW_KEY_STR)
        f_new = Fernet(new_user_key)
        
        data_str = json.dumps(json_data, indent=2)
        new_encrypted_data = f_new.encrypt(data_str.encode('utf-8'))
        
        with open(NOTEBOOKS_FILE, 'wb') as f:
            f.write(new_encrypted_data)
        print("✅ Successfully re-encrypted and saved.")
        
    except Exception as e:
        print(f"❌ Failed to encrypt with new key: {e}")

if __name__ == "__main__":
    reencrypt()
