import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinterdnd2 import TkinterDnD, DND_FILES
from pathlib import Path
import subprocess
import threading
import sys

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Google Takeout Fixer")
        self.geometry("700x450")
        self.configure(bg="#f2f2f2")
        self.resizable(False, False)

        self.folder_path = None
        self.process = None

        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self,
            # text="Kéo & thả thư mục vào vùng bên dưới",
            bg="#f2f2f2",
            font=("Arial", 11)
        ).pack(pady=10)

        # ===== DROP ZONE =====
        self.drop_zone = tk.Canvas(
            self,
            width=500,
            height=90,
            bg="#e8f0fe",
            highlightthickness=0
        )
        self.drop_zone.pack()

        self.rect = self.drop_zone.create_rectangle(
            5, 5, 495, 85,
            outline="#1a73e8",
            width=2,
            dash=(6, 4)
        )

        self.text = self.drop_zone.create_text(
            250, 45,
            text="📁 Kéo & thả thư mục vào đây\nhoặc click để chọn\nDrag and Drop desired folder\nor click here to choose",
            fill="#1a73e8",
            font=("Arial", 11),
            justify="center"
        )

        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind("<<Drop>>", self.on_drop)
        self.drop_zone.bind("<Button-1>", self.select_folder)

        # ===== RUN BUTTON =====
        tk.Button(
            self,
            text="Run",
            width=20,
            relief="solid",
            command=self.run
        ).pack(pady=50)

        # ===== LOG AREA =====
        tk.Label(
            self,
            text="Log output",
            bg="#f2f2f2",
            anchor="w"
        ).pack(fill="x", padx=20)

        self.log_text = ScrolledText(
            self,
            height=12,
            font=("Consolas", 10),
            state="disabled",
            bg="#0d1117",
            fg="#c9d1d9",
            insertbackground="white"
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=10)

    # ================= LOG UTILS =================
    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ================= EVENTS =================
    def on_drop(self, event):
        path = event.data.strip("{}")
        if Path(path).is_dir():
            self.folder_path = path
            self.drop_zone.itemconfig(
                self.text,
                text=f"✅ Đã chọn:\n{path}"
            )
        else:
            messagebox.showerror("Lỗi", "Vui lòng thả thư mục!")

    def select_folder(self, event=None):
        from tkinter import filedialog
        path = filedialog.askdirectory()
        if path:
            self.folder_path = path
            self.drop_zone.itemconfig(
                self.text,
                text=f"✅ Đã chọn:\n{path}"
            )

    # ================= RUN =================
    def run(self):
        if not self.folder_path:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa chọn thư mục!")
            return

        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

        self.log("▶ Running main.py ...")

        thread = threading.Thread(
            target=self.run_process,
            daemon=True
        )
        thread.start()

    def run_process(self):
        try:
            self.process = subprocess.Popen(
                [sys.executable, "main.py", self.folder_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in self.process.stdout:
                self.log(line.rstrip())

            self.process.wait()
            self.log("✔ Process finished")

        except Exception as e:
            self.log(f"❌ Error: {e}")

# ================= MAIN =================
if __name__ == "__main__":
    app = App()
    app.mainloop()
