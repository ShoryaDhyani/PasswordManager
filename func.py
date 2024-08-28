import json
from getpass import getpass
from cryptography.fernet import Fernet, InvalidToken
# import main as mn

import tkinter as tk

root = tk.Tk()  # Create the main application window
root.geometry("300x300")
root.title("Password Manager")

# Widgets that are part of the main window
textf = tk.Entry(root)
label = tk.Label(root, text="Enter Pass")

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
    passwords = load_passwords()
    master_password = get_master_password()

    # For simplicity, let's assume the master password check is basic.
    # In a real application, use a secure authentication mechanism.
    if master_password == "1234":
        while True:
            print("\n1. Add/Update Password")
            print("2. Get Password")
            print("3. Exit")

            choice = input("Enter your choice (1/2/3): ")

            if choice == '1':
                service = input("Enter the service: ")
                username = input("Enter the username: ")
                password = getpass("Enter the password: ")
                add_password(passwords, service, username, password)
            elif choice == '2':
                service = input("Enter the service: ")
                stored_password = get_password(passwords, service)
                if stored_password:
                    print(f"Username: {stored_password['username']}")
                    print(f"Password: {stored_password['password']}")
            elif choice == '3':
                save_passwords(passwords)
                save_key(key)
                print("Password manager closed.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    else:
        print("Incorrect master password. Exiting.")

if __name__ == "__main__":
    main()
    root.mainloop()
