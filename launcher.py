# launcher.py

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading

class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NDS Cheat Browser Launcher")
        self.root.geometry("400x200")

        # Label
        label = ttk.Label(root, text="Select an Application to Launch:", font=("Helvetica", 14))
        label.pack(pady=20)

        # Buttons
        webapp_button = ttk.Button(root, text="Launch Web App", command=self.launch_webapp)
        webapp_button.pack(pady=10)

        gui_button = ttk.Button(root, text="Launch GUI", command=self.launch_gui)
        gui_button.pack(pady=10)

    def launch_webapp(self):
        """Launches the Flask web application."""
        try:
            # Determine the executable path relative to the launcher
            if sys.platform == "win32":
                executable = os.path.join(os.path.dirname(sys.executable), 'NDS_Cheat_Browser_WebApp.exe')
            elif sys.platform == "darwin":
                executable = os.path.join(os.path.dirname(sys.executable), 'NDS_Cheat_Browser_WebApp')
            else:
                executable = os.path.join(os.path.dirname(sys.executable), 'NDS_Cheat_Browser_WebApp')
            
            if not os.path.exists(executable):
                messagebox.showerror("Error", "Web App executable not found.")
                return

            # Launch the executable in a separate thread to keep the launcher responsive
            threading.Thread(target=subprocess.Popen, args=(executable,)).start()
            messagebox.showinfo("Success", "Web App launched successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Web App:\n{e}")

    def launch_gui(self):
        """Launches the Tkinter GUI application."""
        try:
            # Determine the executable path relative to the launcher
            if sys.platform == "win32":
                executable = os.path.join(os.path.dirname(sys.executable), 'NDS_Cheat_Browser_GUI.exe')
            elif sys.platform == "darwin":
                executable = os.path.join(os.path.dirname(sys.executable), 'NDS_Cheat_Browser_GUI')
            else:
                executable = os.path.join(os.path.dirname(sys.executable), 'NDS_Cheat_Browser_GUI')
            
            if not os.path.exists(executable):
                messagebox.showerror("Error", "GUI executable not found.")
                return

            # Launch the executable in a separate thread to keep the launcher responsive
            threading.Thread(target=subprocess.Popen, args=(executable,)).start()
            messagebox.showinfo("Success", "GUI launched successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch GUI:\n{e}")

def main():
    root = tk.Tk()
    app = LauncherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
