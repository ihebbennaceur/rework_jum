import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
import threading

def run_build_data_on_files(filepaths, status_labels, progress_var, progress_bar, btn):
    total = len(filepaths)
    for idx, filepath in enumerate(filepaths):
        status_labels[idx].config(text="En cours...", fg="blue")
        btn.config(state="disabled")
        env = os.environ.copy()
        env['OLD_DATA_JSON'] = filepath
        result = subprocess.run(
            [sys.executable, "build_data.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            env=env,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            status_labels[idx].config(text="Success", fg="green")
        else:
            status_labels[idx].config(text="Erreur", fg="red")
        progress_var.set((idx + 1) / total * 100)
        progress_bar.update()
    btn.config(state="normal")
    messagebox.showinfo("All done")

def select_files():
    filepaths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
    if not filepaths:
        return

    # Nettoyer l'affichage précédent
    for widget in files_frame.winfo_children():
        widget.destroy()

    status_labels = []
    for filepath in filepaths:
        row = tk.Frame(files_frame)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=os.path.basename(filepath), anchor="w", width=50).pack(side="left")
        status = tk.Label(row, text="En attente", fg="gray")
        status.pack(side="left", padx=10)
        status_labels.append(status)

    progress_var.set(0)
    progress_bar.update()

    # Lancer le traitement dans un thread pour ne pas bloquer l'UI
    threading.Thread(
        target=run_build_data_on_files,
        args=(filepaths, status_labels, progress_var, progress_bar, btn),
        daemon=True
    ).start()

root = tk.Tk()
root.title("Lancer build_data.py sur des fichiers JSON")

btn = tk.Button(root, text="Sélectionner un ou plusieurs fichiers JSON", command=select_files)
btn.pack(padx=20, pady=(20, 5))

files_frame = tk.Frame(root)
files_frame.pack(padx=20, pady=5, fill="x")

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill="x", padx=20, pady=(5, 20))

root.mainloop()