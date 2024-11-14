import tkinter as tk
import main as ab

# File paths
key_file_path = 'encryption_key.key'
passwords_file_path = 'passwords.json'
# key = ab.load_key()
# cipher_suite = ab.Fernet(key)

root = tk.Tk()  # Create the main application window
root.geometry("300x300")
root.title("Password Manager")

# Widgets that are part of the main window
textf = tk.Entry(root)
label = tk.Label(root, text="Enter Pass")

def main():
    global passwords
    passwords = ab.load_passwords()
    label.pack(pady=5)
    textf.pack(padx=5)
    butt.pack(pady=5)
    bt3.pack(side=tk.BOTTOM, pady=10)
    root.mainloop()

def save_val():
    val = textf.get()
    if val == "1234":
        textf.destroy()
        label.destroy()
        butt.destroy()
        func1()
    else:
        Openpop_up("Incorrect Password")

def Openpop_up(st: str)->None:
    root.withdraw()
    popup = tk.Toplevel(root)  # Use Toplevel for new windows
    popup.geometry("200x200")
    popup.title(st)
    label = tk.Label(popup, text=st)
    label.pack(pady=10)
    b = tk.Button(popup, text="Ok", command=lambda: [popup.destroy(),root.deiconify()])
    b.pack(pady=10)

def get_pass():
    # bt1.pack_forget()
    # bt2.pack_forget()
    root.withdraw()
    getp = tk.Toplevel(root)  # Use Toplevel for new windows
    getp.geometry("300x300")
    t1 = tk.Label(getp, text="Enter Service")
    t1.pack(pady=5)
    ent1 = tk.Entry(getp)
    ent1.pack(pady=5)
    t2 = tk.Label(getp, text="Enter Username")
    t2.pack(pady=5)
    ent2 = tk.Entry(getp)
    ent2.pack(pady=5)
    t3 = tk.Label(getp, text="Enter Password")
    t3.pack()
    ent3 = tk.Entry(getp)
    ent3.pack(pady=5)
    addb = tk.Button(getp, text="Add", command=lambda: [ab.add_password(passwords, ent1.get(), ent2.get(), ent3.get()),ab.save_passwords(passwords)])
    addb.pack()
    bck = tk.Button(getp, text="Back", command=lambda: [getp.destroy(), func1(),root.deiconify()])
    bck.pack()




def give_val():
    # bt1.pack_forget()
    # bt2.pack_forget()
    root.withdraw()
    getp = tk.Toplevel(root)  # Use Toplevel for new windows
    getp.geometry("300x300")
    t1 = tk.Label(getp, text="Enter Service")
    t1.pack(pady=5)
    ent1 = tk.Entry(getp)
    ent1.pack(pady=5)
    getb = tk.Button(getp, text="Get", command=lambda: [showp(ab.get_password(passwords, ent1.get())),getp.destroy()])
    getb.pack()
    bck = tk.Button(getp, text="Back", command=lambda: [getp.destroy(), func1(),root.deiconify()])
    bck.pack()


def showp(x)->None:
   if x:
      popup = tk.Toplevel(root)  # Use Toplevel for new windows
      popup.geometry("200x200")
      popup.title("Passwords")
      label = tk.Label(popup, text="Username="+x['username'])
      label.pack(pady=10)
      label1 = tk.Label(popup, text="Password= "+x['password'])
      label1.pack(pady=10)
      b = tk.Button(popup, text="Ok", command=lambda:[popup.destroy(),root.deiconify()])
      b.pack(pady=10)
   else :
       Openpop_up("Nothing Found")
       


# Main buttons on the first screen
bt1 = tk.Button(root, text="Add Passwords", command=get_pass)
bt2 = tk.Button(root, text="Get Passwords", command=give_val)
bt3 = tk.Button(root, text="Exit", command=lambda:[root.destroy(),ab.save_key(ab.key),ab.save_passwords(passwords)])
butt = tk.Button(root, text="Next", command=save_val)

def func1():
    bt1.pack(padx=10, pady=5)
    bt2.pack(padx=10, pady=5)
    bt3.pack(padx=10, pady=5)

# if __name__ == "__main__":
#     ab.main()  # Initialize the UI
    # root.mainloop()  # Start the Tkinter event loop
