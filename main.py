import json
from getpass import getpass
from cryptography.fernet import Fernet, InvalidToken
import ui as mn

key_file_path = 'encryption_key.key'
passwords_file_path = 'passwords.json'

def generate_key():
    return Fernet.generate_key()

def load_key():
    try:
        with open(key_file_path, 'rb') as key_file:
            return key_file.read()
    except FileNotFoundError:
        return generate_key()

def save_key(key):
    with open(key_file_path, 'wb') as key_file:
        key_file.write(key)

def load_passwords():
    try:
        with open(passwords_file_path, 'rb') as file:
            encrypted_passwords = file.read()
            decrypted_passwords = cipher_suite.decrypt(encrypted_passwords)
            passwords = json.loads(decrypted_passwords.decode())
    except (FileNotFoundError, json.JSONDecodeError, InvalidToken):
        passwords = {}
    return passwords

def save_passwords(passwords):
    encrypted_passwords = cipher_suite.encrypt(json.dumps(passwords).encode())
    with open(passwords_file_path, 'wb') as file:
        file.write(encrypted_passwords)

# Main code starts here
key = load_key()
cipher_suite = Fernet(key)

def get_master_password():
    return getpass("Enter your master password: ")

def add_password(passwords, service, username, password):
    if service in passwords:
        print(f"Password for {service} already exists. Updating.")
    passwords[service] = {'username': username, 'password': password}
    print(f"Password for {service} added/updated successfully.")

def get_password(passwords, service):
    if service in passwords:
        return passwords[service]
    else:
        print(f"No password found for {service}.")
        return None

def main():
    mn.main()


if __name__ == "__main__":
    main()
