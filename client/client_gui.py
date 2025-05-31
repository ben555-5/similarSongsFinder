import socket
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from utils.caesar_cipher import caesar_decrypt, caesar_encrypt
from database import add_user, verify_user


HOST = '127.0.0.1'
PORT = 65432

class SongRecommenderApp:
    def __init__(self, master):
        self.master = master
        master.title("Song Recommender")
        master.geometry("320x220")

        self.user_id = None
        self.sock = None

        self.build_login_ui()

    def build_login_ui(self):
        self.login_frame = tk.Frame(self.master)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0, sticky="e")
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky="e")
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        self.login_btn = tk.Button(self.login_frame, text="Login", width=10, command=self.login)
        self.login_btn.grid(row=2, column=0, pady=10)

        self.signup_btn = tk.Button(self.login_frame, text="Sign Up", width=10, command=self.signup)
        self.signup_btn.grid(row=2, column=1, pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Missing Info", "Please enter both username and password.")
            return

        user_id = verify_user(username, password)
        if user_id:
            self.user_id = user_id
            messagebox.showinfo("Login Approved", f"Welcome back, {username}!")  # ✅
            self.connect_to_server()
            self.show_main_ui()
        else:
            messagebox.showerror("Login Rejected", "Invalid username or password.")  # ❌

    def signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Missing Info", "Please enter both username and password.")
            return

        success = add_user(username, password)
        if success:
            self.user_id = verify_user(username, password)
            messagebox.showinfo("Signup Approved", f"Welcome, {username}!")  # ✅
            self.connect_to_server()
            self.show_main_ui()
        else:
            messagebox.showerror("Signup Failed", "Username already exists.")  # ❌

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")
            self.master.destroy()

    def show_main_ui(self):
        self.login_frame.destroy()

        self.label = tk.Label(self.master, text="Enter a song name:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(self.master, width=30)
        self.entry.pack()

        self.search_button = tk.Button(self.master, text="Search", command=self.search_song)
        self.search_button.pack(pady=10)

        self.loading_label = tk.Label(self.master, text="", fg="blue")
        self.loading_label.pack()

    def send(self, msg):
        try:
            encrypted = caesar_encrypt(msg)
            self.sock.sendall(encrypted.encode())
            response_encrypted = self.sock.recv(65536).decode()
            decrypted = caesar_decrypt(response_encrypted)
            return json.loads(decrypted)
        except Exception as e:
            messagebox.showerror("Communication Error", f"Failed to communicate with server:\n{e}")
            return []

    def search_song(self):
        query = self.entry.get().strip()
        if not query:
            messagebox.showinfo("Missing Input", "Please enter a song name.")
            return

        self.loading_label.config(text="🔄 Searching...")
        self.master.update_idletasks()

        options = self.send(f"SEARCH:{query}")
        self.loading_label.config(text="")

        if not options:
            messagebox.showinfo("No Matches", "No matching songs found.")
            return

        choice_text = "\n".join([f"{i+1}. {opt[1]}" for i, opt in enumerate(options)])
        choice = tk.simpledialog.askinteger("Choose Song", choice_text + "\n\nEnter number (1-10):")
        if not choice or choice < 1 or choice > len(options):
            return

        self.loading_label.config(text="🎧 Finding similar songs...")
        self.master.update_idletasks()

        selected_track_id = options[choice - 1][0]
        matches = self.send(selected_track_id)
        self.loading_label.config(text="")

        if matches:
            result_text = "\n".join(matches)
            messagebox.showinfo("Top Matches", result_text)
        else:
            messagebox.showinfo("No Matches", "No similar songs found.")

    def close(self):
        try:
            if self.sock:
                self.sock.close()
        except:
            pass
        self.master.destroy()
