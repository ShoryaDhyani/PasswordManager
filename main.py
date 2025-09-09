import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import aws as aw 

aws_client = aw.AWSStorage()

BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4a7abc"
TEXT_COLOR = "#333333"
TITLE_FONT = ("Arial", 16, "bold")
LABEL_FONT = ("Arial", 12)
BUTTON_FONT = ("Arial", 10, "bold")

class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("500x400")
        self.root.configure(bg=BG_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.current_user = None
        self.passwords = {}
        
        self.show_login_screen()
        root.report_callback_exception = self.handle_tkinter_error
    def handle_tkinter_error(self, exc, val, tb):
        """Handle Tkinter callback exceptions"""
        error_msg = f"Tkinter Error: {str(val)}\n{exc.__name__}"
        print(error_msg)
        messagebox.showerror("Application Error", error_msg)
    
    def clear_frame(self):
        """Clear all widgets from the root window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display the login/signup screen"""
        self.clear_frame()
        
        # Title
        tk.Label(self.root, text="Password Manager", font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        # Username
        tk.Label(self.root, text="Username:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        self.username_entry = tk.Entry(self.root, font=LABEL_FONT)
        self.username_entry.pack(pady=5)
        self.username_entry.focus_set()
        
        # Password
        tk.Label(self.root, text="Password:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", font=LABEL_FONT)
        self.password_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.root, bg=BG_COLOR)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Login", command=self.handle_login, 
                  bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT, padx=10, pady=5).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Sign Up", command=self.handle_signup, 
                  bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT, padx=10, pady=5).pack(side=tk.LEFT, padx=10)
        
        tk.Button(self.root, text="Exit", command=self.root.destroy, 
                  bg="#e74c3c", fg="white", font=BUTTON_FONT, padx=10, pady=5).pack(pady=10)
    
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required.")
            return
        
        try:
            tokens = aws_client.login(username, password)
            self.current_user = username
            # For demo, we use the login password as master password to decrypt data
            self.passwords = aws_client.load_user_data(username, password)
            self.show_main_screen()
        except Exception as e:
            messagebox.showerror("Login Failed", f"Error: {str(e)}")
        try:
            tokens = aws_client.login(username, password)
            self.current_user = username
            self.passwords = aws_client.load_user_data(username, password)

            # Ensure passwords is always a dictionary
            if self.passwords is None:
                self.passwords = {}

            self.show_main_screen()
        except Exception as e:
            messagebox.showerror("Login Failed", str(e))
    
    def handle_signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required.")
            return
        
        email = simpledialog.askstring("Sign Up", "Enter your email:", parent=self.root)
        if not email:
            return
        
        try:
            aws_client.sign_up(username, password, email)
            code = simpledialog.askstring("Confirmation", "Enter the confirmation code sent to your email:", parent=self.root)
            if code:
                aws_client.confirm_sign_up(username, code)
                messagebox.showinfo("Success", "Account created successfully! Please log in.")
        except Exception as e:
            messagebox.showerror("Signup Failed", str(e))
    
    def show_main_screen(self):
        """Show the main menu after login"""
        self.clear_frame()
        
        tk.Label(self.root, text=f"Welcome, {self.current_user}", font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=20)
        
        button_frame = tk.Frame(self.root, bg=BG_COLOR)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Add Password", command=self.add_password_screen, 
                  bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT, width=15, pady=5).pack(pady=10)
        
        tk.Button(button_frame, text="Get Password", command=self.get_password_screen, 
                  bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT, width=15, pady=5).pack(pady=10)
        
        tk.Button(button_frame, text="List All Passwords", command=self.list_passwords_screen, 
                  bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT, width=15, pady=5).pack(pady=10)
        
        tk.Button(button_frame, text="Logout", command=self.logout, 
                  bg="#e74c3c", fg="white", font=BUTTON_FONT, width=15, pady=5).pack(pady=20)
    
    def add_password_screen(self):
        """Screen for adding a new password entry"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Password")
        dialog.geometry("400x350")
        dialog.configure(bg=BG_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()

        # Create a flag to track if we're in the process of closing
        dialog.closing = False

        tk.Label(dialog, text="Add New Credentials", font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

        tk.Label(dialog, text="Service/App:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        service_entry = tk.Entry(dialog, font=LABEL_FONT)
        service_entry.pack(pady=5)

        tk.Label(dialog, text="Username:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        username_entry = tk.Entry(dialog, font=LABEL_FONT)
        username_entry.pack(pady=5)

        tk.Label(dialog, text="Password:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        password_entry = tk.Entry(dialog, show="*", font=LABEL_FONT)
        password_entry.pack(pady=5)

        def on_close():
            dialog.closing = True
            dialog.destroy()

        def save():
            # Check if dialog is closing to prevent race conditions
            if dialog.closing:
                return

            service = service_entry.get().strip()
            username_val = username_entry.get().strip()
            password_val = password_entry.get()

            if not service or not username_val or not password_val:
                messagebox.showerror("Error", "All fields are required.", parent=dialog)
                return

            try:
                # Add the password
                if service not in self.passwords:
                    self.passwords[service] = {}
                self.passwords[service][username_val] = password_val
                dia = tk.Toplevel(self.root)
                dia.title("Verify")
                dia.geometry("200x100")
                dia.configure(bg=BG_COLOR)
                dia.transient(self.root)
                dia.grab_set()
                pss = tk.Entry(dia, show="*", font=LABEL_FONT)
                btn = tk.Button(dia, text="Verify", command=lambda: blabla(), bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT, padx=10)
                btn.pack(pady=10)
                tk.Label(dia, text="Enter Password:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
                pss.pack(pady=10)
                pss.focus_set()
                # Save to AWS
                def blabla():
                    if aws_client.verify_password(pss.get()):
                        aws_client.save_user_data(self.current_user, self.passwords, pss.get())
                        messagebox.showinfo("Success", "Password added successfully!", parent=self.root)
                        dia.destroy()
                        dialog.closing = True
                        dialog.destroy()
                        messagebox.showinfo("Success", "Password added successfully!", parent=self.root)
                    else:
                        messagebox.showerror("Error", "Incorrect password. Please try again.", parent=dia)
                        save()
                        return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}", parent=dialog)

        button_frame = tk.Frame(dialog, bg=BG_COLOR)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Save", command=save,
                  bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT, padx=10)\
            .pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Cancel", command=on_close,
                  bg="#95a5a6", fg="white", font=BUTTON_FONT, padx=10)\
            .pack(side=tk.LEFT, padx=10)

        # Handle window close properly
        dialog.protocol("WM_DELETE_WINDOW", on_close)

    def get_password_screen(self):
        """Screen for retrieving a password"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Get Password")
        dialog.geometry("400x250")
        dialog.configure(bg=BG_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Retrieve Credentials", font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)
        
        # Service
        tk.Label(dialog, text="Service/App:", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        service_entry = tk.Entry(dialog, font=LABEL_FONT)
        service_entry.pack(pady=5)
        
        # Username (optional)
        tk.Label(dialog, text="Username (optional):", font=LABEL_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        username_entry = tk.Entry(dialog, font=LABEL_FONT)
        username_entry.pack(pady=5)
        
        def retrieve():
            service = service_entry.get().strip()
            if not service:
                messagebox.showerror("Error", "Service is required.", parent=dialog)
                return
            
            username_val = username_entry.get().strip() or None
            if service not in self.passwords:
                result = None
            elif username_val:
                result = self.passwords[service].get(username_val)
            else:
                result = self.passwords[service]
            if result is None:
                messagebox.showinfo("Not Found", "No credentials found for this service.", parent=dialog)
            elif isinstance(result, str):
                messagebox.showinfo("Credentials", f"Password: {result}", parent=dialog)
            else:
                # Multiple credentials
                message = "Credentials:\n\n"
                for uname, pwd in result.items():
                    message += f"Username: {uname}\nPassword: {pwd}\n\n"
                messagebox.showinfo("Credentials", message, parent=dialog)
        
        button_frame = tk.Frame(dialog, bg=BG_COLOR)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Retrieve", command=retrieve, bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT, padx=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg="#95a5a6", fg="white", font=BUTTON_FONT, padx=10).pack(side=tk.LEFT, padx=10)
    
    def list_passwords_screen(self):
        """Display all passwords in a new window"""
        dialog = tk.Toplevel(self.root)
        dialog.title("All Passwords")
        dialog.geometry("600x500")
        dialog.configure(bg=BG_COLOR)
        
        frame = tk.Frame(dialog, bg=BG_COLOR)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area = tk.Text(frame, yscrollcommand=scrollbar.set, wrap=tk.WORD, bg="white", fg=TEXT_COLOR, font=LABEL_FONT, padx=10, pady=10)
        text_area.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_area.yview)
        
        if not self.passwords:
            text_area.insert(tk.END, "No passwords stored yet.")
        else:
            for service, creds in self.passwords.items():
                text_area.insert(tk.END, f"Service: {service}\n")
                for username, password in creds.items():
                    text_area.insert(tk.END, f"  Username: {username}\n")
                    text_area.insert(tk.END, f"  Password: {password}\n")
                text_area.insert(tk.END, "-" * 50 + "\n")
        
        text_area.config(state=tk.DISABLED)
        
        tk.Button(dialog, text="Close", command=dialog.destroy, bg=BUTTON_COLOR, fg="white", 
                  font=BUTTON_FONT, padx=10, pady=5).pack(pady=10)
    
    def logout(self):
        """Log out the current user"""
        self.current_user = None
        self.passwords = {}
        self.show_login_screen()
    
    def on_closing(self):
        """Handle window closing event"""
        # In a real app, you might save data here
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()