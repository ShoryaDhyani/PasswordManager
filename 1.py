import json
from getpass import getpass

def load_passwords(filename='passwords.json'):
    try:
        with open(filename, 'r') as file:
            passwords = json.load(file)
    except FileNotFoundError:
        passwords = {}
    return passwords

def save_passwords(passwords, filename='passwords.json'):
    with open(filename, 'w') as file:
        json.dump(passwords, file, indent=2)

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
                print("Password manager closed.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    else:
        print("Incorrect master password. Exiting.")

if __name__ == "__main__":
    main()
