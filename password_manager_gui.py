import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import json
import os

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
            file.write('\n')  # Add a newline for better readability between entries

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

        # Buttons
        self.add_button = tk.Button(self.window, text="Add Password", command=self.add_password)
        self.search_button = tk.Button(self.window, text="Search Password", command=self.search_password)

        # Layout
        self.website_entry.grid(row=0, column=1, padx=10, pady=5)
        self.username_entry.grid(row=1, column=1, padx=10, pady=5)
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.window, text="Website:").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(self.window, text="Username:").grid(row=1, column=0, padx=10, pady=5)
        tk.Label(self.window, text="Password:").grid(row=2, column=0, padx=10, pady=5)

        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.search_button.grid(row=4, column=0, columnspan=2, pady=10)

    def add_password(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if website and username and password:
            self.password_manager.add_password(website, username, password)
            messagebox.showinfo("Success", "Password added successfully!")
        else:
            messagebox.showwarning("Incomplete Information", "Please fill in all fields.")

    def search_password(self):
        website_to_search = self.website_entry.get()

        if website_to_search:
            result = self.password_manager.search_password(website_to_search)
            messagebox.showinfo("Search Result", result)
        else:
            messagebox.showwarning("Incomplete Information", "Please enter a website to search.")

    def run(self):
        self.window.mainloop()

# Example Usage
password_manager = PasswordManager()
gui = PasswordManagerGUI(password_manager)
gui.run()
