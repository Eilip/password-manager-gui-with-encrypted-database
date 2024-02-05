import tkinter as tk
from tkinter import scrolledtext, messagebox
from cryptography.fernet import Fernet
import json
import os
from PIL import Image, ImageTk

class PasswordManager:
    def __init__(self, key_file='key.key', data_file='passwords.json'):
        self.key_file = key_file
        self.data_file = data_file
        self.load_or_generate_key()

    def load_or_generate_key(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)

        with open(self.key_file, 'rb') as key_file:
            self.key = key_file.read()

    def encrypt_password(self, password):
        cipher_suite = Fernet(self.key)
        encrypted_password = cipher_suite.encrypt(password.encode())
        return encrypted_password

    def decrypt_password(self, encrypted_password):
        cipher_suite = Fernet(self.key)
        decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
        return decrypted_password

    def load_passwords(self):
        data = {}
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                try:
                    data = json.load(file)
                except json.decoder.JSONDecodeError:
                    pass
        return data

    def save_passwords(self, data):
        try:
            with open(self.data_file, 'r') as file:
                existing_data = json.load(file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            existing_data = {}

        existing_data.update(data)

        with open(self.data_file, 'w') as file:
            json.dump(existing_data, file, indent=2, default=lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
            file.write('\n')

    def generate_password(self, length=12):
        import secrets
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        return password

    def add_password(self, website, username, password):
        data = self.load_passwords()
        encrypted_password = self.encrypt_password(password)
        data[website] = {'username': username, 'password': encrypted_password}
        self.save_passwords(data)

    def search_password(self, website):
        data = self.load_passwords()
        for stored_website, values in data.items():
            if stored_website.lower() == website.lower():
                encrypted_password = values['password']
                decrypted_password = self.decrypt_password(encrypted_password)
                username = values['username']
                return f"Website: {stored_website}\nUsername: {username}\nPassword: {decrypted_password}"

        return "Password not found for the given website."

class PasswordManagerGUI:
    def __init__(self, password_manager):
        self.password_manager = password_manager

        self.window = tk.Tk()
        self.window.title("Password Manager")

        # Entry fields
        self.website_entry = tk.Entry(self.window, width=30)
        self.username_entry = tk.Entry(self.window, width=30)
        self.password_entry = tk.Entry(self.window, width=30, show='*')

        # ScrolledText for output entry
        self.output_entry = scrolledtext.ScrolledText(self.window, width=70, height=15, background='white',  wrap=tk.WORD)
        self.output_entry.place(x=50, y=20)

        

        # Buttons
        self.add_button = tk.Button(self.window, text="Add Password", command=self.add_password, fg='white', background="orange")
        self.search_button = tk.Button(self.window, text="Search Password", command=self.search_password)
        self.generate_password_button = tk.Button(self.window, text="Generate Password", command=self.generate_password)
        self.copy_password_button = tk.Button(self.window, text="Copy Password", command=self.copy_password)
        self.copy_username_button = tk.Button(self.window, text="Copy Username", command=self.copy_username)

        # Layout
        self.website_entry.grid(row=0, column=1, padx=10, pady=5)
        self.username_entry.grid(row=1, column=1, padx=10, pady=5)
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)
        tk.Label(self.window, text="Website:").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(self.window, text="Username:").grid(row=1, column=0, padx=10, pady=5)
        tk.Label(self.window, text="Password:").grid(row=2, column=0, padx=10, pady=5)

        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.search_button.grid(row=4, column=0, columnspan=2, pady=10)
        self.generate_password_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.output_entry.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="w")  # Output entry
        self.copy_password_button.grid(row=7, column=0, pady=10)
        self.copy_username_button.grid(row=7, column=1, pady=10)

    def add_password(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if website and username and password:
            self.password_manager.add_password(website, username, password)
            messagebox.showinfo("Success", "Password added successfully!")
            self.clear_entries()  # Clear input entries after adding password
        else:
            messagebox.showwarning("Incomplete Information", "Please fill in all fields.")

    def search_password(self):
        website_to_search = self.website_entry.get()

        if website_to_search:
            result = self.password_manager.search_password(website_to_search)
            self.display_result(result)
        else:
            messagebox.showwarning("Incomplete Information", "Please enter a website to search.")

    def generate_password(self):
        generated_password = self.password_manager.generate_password()
        self.password_entry.delete(0, tk.END)  # Clear existing content
        self.password_entry.insert(0, generated_password)

    def copy_password(self):
        result = self.output_entry.get("1.0", tk.END)
        password_line = [line for line in result.split('\n') if line.startswith('Password:')]
        if password_line:
            password = password_line[0].split(': ')[1]
            self.window.clipboard_clear()
            self.window.clipboard_append(password)
            self.window.update()
            messagebox.showinfo("Copy", "Password copied to clipboard.")
        else:
            messagebox.showinfo("Copy", "No password to copy.")

    def copy_username(self):
        result = self.output_entry.get("1.0", tk.END)
        username_line = [line for line in result.split('\n') if line.startswith('Username:')]
        if username_line:
            username = username_line[0].split(': ')[1]
            self.window.clipboard_clear()
            self.window.clipboard_append(username)
            self.window.update()
            messagebox.showinfo("Copy", "Username copied to clipboard.")
        else:
            messagebox.showinfo("Copy", "No username to copy.")

    def clear_entries(self):
        # Clear all input entries
        self.website_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def display_result(self, result):
       lines = result.split('\n')
       for line in lines:
           if line.startswith('Password not found'):
               self.output_entry.insert(tk.END, line + '\n')
           elif line.startswith('Website:'):
               self.output_entry.insert(tk.END, line + '\n')
           elif line.startswith('Username:'):
               self.output_entry.insert(tk.END, line + '\n')
           elif line.startswith('Password:'):
               self.output_entry.insert(tk.END, line + '\n')
         


    def run(self):
        self.window.mainloop()

# Example Usage
password_manager = PasswordManager()
gui = PasswordManagerGUI(password_manager)
gui.run()
