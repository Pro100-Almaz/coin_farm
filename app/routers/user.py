import os
import hashlib


def hash_password_with_salt(password: str) -> str:
    salt = os.urandom(16)  # Generate a random salt
    sha256 = hashlib.sha256()
    sha256.update(salt + password.encode('utf-8'))
    hashed_password = salt.hex() + sha256.hexdigest()  # Store the salt along with the hash
    return hashed_password

def verify_password_with_salt(stored_hash: str, password: str) -> bool:
    salt = bytes.fromhex(stored_hash[:32])  # Extract the salt from the stored hash
    stored_hash = stored_hash[32:]
    sha256 = hashlib.sha256()
    sha256.update(salt + password.encode('utf-8'))
    return sha256.hexdigest() == stored_hash


password = "mysecretpassword"
hashed_password_with_salt = hash_password_with_salt(password)
print("Hashed Password with Salt:", hashed_password_with_salt)
print("Verification:", verify_password_with_salt(hashed_password_with_salt, "mysecretpassword"))  # Should print: True
print("Verification:", verify_password_with_salt(hashed_password_with_salt, "wrongpassword"))    # Should print: False

