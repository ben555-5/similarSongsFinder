import socket
import json
import tkinter as tk
from tkinter import simpledialog, messagebox
from utils.caesar_cipher import caesar_decrypt, caesar_encrypt


HOST = '127.0.0.1'
PORT = 65432

class SongRecommenderApp:
    def __init__(self, master):
        self.master = master
        master.title("Song Recommender")
        master.geometry("300x180")

        self.label = tk.Label(master, text="Enter a song name:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(master, width=30)
        self.entry.pack()

        self.search_button = tk.Button(master, text="Search", command=self.search_song)
        self.search_button.pack(pady=10)

        # Loading label (hidden by default)
        self.loading_label = tk.Label(master, text="", fg="blue")
        self.loading_label.pack()

        # open socket once
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")
            master.destroy()

    def send(self, msg):
        try:
            msg = caesar_encrypt(msg)
            self.sock.sendall(msg.encode())
            decrypted_msg = self.sock.recv(65536).decode()
            return json.loads(decrypted_msg)
        except Exception as e:
            messagebox.showerror("Communication Error", f"Failed to communicate with server:\n{e}")
            return []

    def search_song(self):
        query = self.entry.get().strip()
        if not query:
            messagebox.showinfo("Missing Input", "Please enter a song name.")
            return

        self.loading_label.config(text="🔄 Searching...")
        self.master.update_idletasks()  # Refresh UI

        options = self.send(f"SEARCH:{query}")
        self.loading_label.config(text="")  # Hide loading

        if not options:
            messagebox.showinfo("No Matches", "No matching songs found.")
            return

        choice_text = "\n".join([f"{i+1}. {opt[1]}" for i, opt in enumerate(options)])
        choice = simpledialog.askinteger("Choose Song", choice_text + "\n\nEnter number (1-10):")
        if not choice or choice < 1 or choice > len(options):
            return

        self.loading_label.config(text="🎧 Finding similar songs...")
        self.master.update_idletasks()

        selected_track_id = options[choice - 1][0]
        matches = self.send(f"CONFIRM:{selected_track_id}")
        self.loading_label.config(text="")  # Hide again

        if matches:
            result_text = "\n".join(matches)
            messagebox.showinfo("Top Matches", result_text)
        else:
            messagebox.showinfo("No Matches", "No similar songs found.")

    def close(self):
        try:
            self.sock.close()
        except:
            pass
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SongRecommenderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


