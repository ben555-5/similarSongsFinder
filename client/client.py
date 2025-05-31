# client.py

import tkinter as tk
from client_gui import SongRecommenderApp

if __name__ == "__main__":
    root = tk.Tk()
    app = SongRecommenderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


