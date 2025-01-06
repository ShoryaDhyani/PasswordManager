# Password Manager

A simple password manager built with Python and Tkinter, using encryption for secure storage.

## Features
- Add and save passwords securely.
- Retrieve saved passwords.
- Encrypted password storage using the `cryptography` library.

---

## Requirements

Before running the application, ensure you have the following installed:
- Python 3.7 or higher
- Required Python libraries (see `requirements.txt`)

---

## Installation and Setup

### 1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone <repository_url>
cd <project_directory>
```

### 2. Install Dependencies
Install the required Python libraries:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Run the application using:
```bash
python main.py
```
or Run PasswordManager.exe file.

---

## Creating an Executable File

To create an executable file for running the application without Python, use `PyInstaller`:

### 1. Install PyInstaller
Install PyInstaller with:
```bash
pip install pyinstaller
```

### 2. Generate the Executable
Run the following command to generate an `.exe` file:
```bash
pyinstaller --onefile --windowed main.py
```
- `--onefile`: Creates a single executable file.
- `--windowed`: Ensures no console window opens with the GUI.

The `.exe` file will be located in the `dist/` directory.

---

## Running the Executable

1. Navigate to the `dist/` directory:
   ```bash
   cd dist
   ```
2. Run the executable file:
   ```bash
   ./main.exe
   ```

---

## Notes
- Ensure that `encryption_key.key` and `passwords.json` are in the same directory as the `.exe` file.
- If the files do not exist, the application will create them automatically.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

