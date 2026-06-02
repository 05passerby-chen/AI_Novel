# backend/launcher.py
# -*- coding: utf-8 -*-
"""
AI Novel Editor — Desktop Launcher EXE

Reads .env (created by install_deps.exe) to find Python and paths.
Starts the FastAPI backend and serves the frontend.
"""
import sys
import os
import subprocess
import threading
import queue
import time
import json
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ─── Paths (handle both source and PyInstaller frozen) ─────────────
if getattr(sys, 'frozen', False):
    _EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    _EXE_DIR = os.path.dirname(os.path.abspath(__file__))

# The backend directory — try exe dir first (source run from backend/),
# then exe_dir/backend (exe placed at project root)
if os.path.exists(os.path.join(_EXE_DIR, "main.py")):
    ROOT = _EXE_DIR
else:
    ROOT = os.path.join(_EXE_DIR, "backend")

ENV_FILE = os.path.join(ROOT, ".env")
SETTINGS_FILE = os.path.join(ROOT, "launcher_settings.json")
FRONTEND_DIST = os.path.join(os.path.dirname(ROOT), "dist")
DEFAULT_PORT = 8765
DEFAULT_NOVELS_DIR = os.path.join(os.path.expanduser("~"), "Novels")


def load_env():
    """Read .env file into a dict."""
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env[key.strip()] = val.strip()
    return env


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"save_path": DEFAULT_NOVELS_DIR, "port": DEFAULT_PORT}


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# ─── Backend Manager ──────────────────────────────────────────────

class BackendManager:
    def __init__(self, log_queue: queue.Queue):
        self.process = None
        self.log_queue = log_queue
        self.running = False

    def start(self, python_path: str, backend_dir: str, port: int):
        if self.running:
            return
        self.running = True

        def run():
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            self.process = subprocess.Popen(
                [python_path, "main.py", "--port", str(port)],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            for line in iter(self.process.stdout.readline, ""):
                self.log_queue.put(("log", line.rstrip()))
            self.process.stdout.close()
            rc = self.process.wait()
            self.log_queue.put(("status", f"Backend exited with code {rc}"))
            self.running = False

        threading.Thread(target=run, daemon=True).start()

    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.running = False
            self.log_queue.put(("log", "Backend stopped."))


# ─── Main Window ──────────────────────────────────────────────────

class LauncherApp:
    def __init__(self):
        self.env = load_env()
        self.settings = load_settings()
        self.log_queue = queue.Queue()
        self.backend = BackendManager(self.log_queue)

        # Check .env
        self.python_path = self.env.get("PYTHON_PATH", sys.executable)
        self.backend_dir = self.env.get("BACKEND_DIR", ROOT)

        self.root = tk.Tk()
        self.root.title("AI Novel Editor — Launcher")
        self.root.geometry("860x600")
        self.root.minsize(700, 450)
        self.root.configure(bg="#0d1117")
        try:
            icon = os.path.join(os.path.dirname(ROOT), "icon.ico")
            if os.path.exists(icon):
                self.root.iconbitmap(icon)
        except Exception:
            pass

        self._build_ui()
        self._poll_log()

        # If .env exists, auto-start
        if os.path.exists(ENV_FILE):
            self._append_log("✓ .env found. Ready to start.")
        else:
            self._append_log("⚠ .env not found. Please run install_deps.exe first.")

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ── Left Sidebar ──
        sidebar = tk.Frame(paned, bg="#161b22", width=320)
        paned.add(sidebar, weight=0)

        hf = tk.Frame(sidebar, bg="#161b22")
        hf.pack(fill=tk.X, padx=12, pady=(12, 6))
        tk.Label(hf, text="📋 Log", font=("Microsoft YaHei", 11, "bold"),
                 fg="#58a6ff", bg="#161b22").pack(side=tk.LEFT)
        self.status_label = tk.Label(hf, text="● Stopped", font=("Microsoft YaHei", 9),
                                      fg="#f85149", bg="#161b22")
        self.status_label.pack(side=tk.RIGHT)

        lf = tk.Frame(sidebar, bg="#0d1117")
        lf.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.log_text = scrolledtext.ScrolledText(
            lf, wrap=tk.WORD, font=("Consolas", 9),
            bg="#0d1117", fg="#c9d1d9", insertbackground="#c9d1d9",
            relief=tk.FLAT, borderwidth=0, highlightthickness=0,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)

        clear_btn = tk.Button(sidebar, text="Clear Log", font=("Microsoft YaHei", 9),
                              bg="#21262d", fg="#c9d1d9", relief=tk.FLAT,
                              activebackground="#30363d", activeforeground="#fff",
                              command=self._clear_log, cursor="hand2")
        clear_btn.pack(fill=tk.X, padx=8, pady=(0, 8))

        # ── Right Main ──
        main = tk.Frame(paned, bg="#0d1117")
        paned.add(main, weight=1)

        tf = tk.Frame(main, bg="#0d1117")
        tf.pack(fill=tk.X, padx=20, pady=(30, 20))
        tk.Label(tf, text="📖 AI Novel Editor", font=("Microsoft YaHei", 22, "bold"),
                 fg="#e6edf3", bg="#0d1117").pack(anchor=tk.W)
        tk.Label(tf, text="AI-powered long-form fiction creation tool",
                 font=("Microsoft YaHei", 10), fg="#8b949e", bg="#0d1117").pack(anchor=tk.W, pady=(4, 0))

        # Env info
        env_card = tk.Frame(main, bg="#161b22", highlightthickness=1, highlightbackground="#30363d")
        env_card.pack(fill=tk.X, padx=20, pady=(0, 12))
        env_info = tk.Frame(env_card, bg="#161b22")
        env_info.pack(fill=tk.X, padx=16, pady=(12, 12))
        tk.Label(env_info, text=f"Python: {self.python_path}", font=("Consolas", 9),
                 fg="#8b949e", bg="#161b22").pack(anchor=tk.W)
        tk.Label(env_info, text=f"Backend: {self.backend_dir}", font=("Consolas", 9),
                 fg="#8b949e", bg="#161b22").pack(anchor=tk.W)
        tk.Label(env_info, text=f"Frontend: {FRONTEND_DIST} {'✓' if os.path.exists(os.path.join(FRONTEND_DIST, 'index.html')) else '✗'}",
                 font=("Consolas", 9), fg="#8b949e", bg="#161b22").pack(anchor=tk.W)

        # Settings card
        card = tk.Frame(main, bg="#161b22", highlightthickness=1, highlightbackground="#30363d")
        card.pack(fill=tk.X, padx=20, pady=(0, 12))

        pf = tk.Frame(card, bg="#161b22")
        pf.pack(fill=tk.X, padx=16, pady=(16, 8))
        tk.Label(pf, text="Novels Directory", font=("Microsoft YaHei", 10),
                 fg="#8b949e", bg="#161b22").pack(anchor=tk.W)
        pr = tk.Frame(pf, bg="#161b22")
        pr.pack(fill=tk.X, pady=(4, 0))
        self.path_var = tk.StringVar(value=self.settings.get("save_path", DEFAULT_NOVELS_DIR))
        tk.Entry(pr, textvariable=self.path_var, font=("Microsoft YaHei", 10),
                 bg="#0d1117", fg="#c9d1d9", relief=tk.FLAT, insertbackground="#c9d1d9",
                 ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 8))
        tk.Button(pr, text="Browse", font=("Microsoft YaHei", 9),
                  bg="#21262d", fg="#c9d1d9", relief=tk.FLAT,
                  activebackground="#30363d", activeforeground="#fff",
                  command=self._browse, cursor="hand2").pack(side=tk.RIGHT, ipadx=8, ipady=2)

        pof = tk.Frame(card, bg="#161b22")
        pof.pack(fill=tk.X, padx=16, pady=(0, 16))
        tk.Label(pof, text="Port", font=("Microsoft YaHei", 10),
                 fg="#8b949e", bg="#161b22").pack(anchor=tk.W)
        self.port_var = tk.StringVar(value=str(self.settings.get("port", DEFAULT_PORT)))
        tk.Entry(pof, textvariable=self.port_var, font=("Microsoft YaHei", 10),
                 bg="#0d1117", fg="#c9d1d9", relief=tk.FLAT, insertbackground="#c9d1d9",
                 width=8).pack(anchor=tk.W, ipady=4, pady=(4, 0))

        # Buttons
        bf = tk.Frame(main, bg="#0d1117")
        bf.pack(fill=tk.X, padx=20, pady=(4, 0))

        self.start_btn = tk.Button(bf, text="▶  Start Server", font=("Microsoft YaHei", 11, "bold"),
                                   bg="#238636", fg="#fff", relief=tk.FLAT,
                                   activebackground="#2ea043", activeforeground="#fff",
                                   command=self._start, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, ipadx=20, ipady=6)

        self.open_btn = tk.Button(bf, text="🌐 Open Browser", font=("Microsoft YaHei", 10),
                                  bg="#21262d", fg="#c9d1d9", relief=tk.FLAT,
                                  activebackground="#30363d", activeforeground="#fff",
                                  command=self._open_browser, cursor="hand2", state=tk.DISABLED)
        self.open_btn.pack(side=tk.LEFT, padx=(12, 0), ipadx=12, ipady=4)

        self.stop_btn = tk.Button(bf, text="⏹ Stop", font=("Microsoft YaHei", 10),
                                  bg="#da3633", fg="#fff", relief=tk.FLAT,
                                  activebackground="#f85149", activeforeground="#fff",
                                  command=self._stop, cursor="hand2", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.RIGHT, ipadx=12, ipady=4)

        # Info
        inf = tk.Frame(main, bg="#0d1117")
        inf.pack(fill=tk.X, padx=20, pady=(20, 0))
        tk.Label(inf, text=f"After clicking Start, open http://127.0.0.1:{self.port_var.get()}",
                 font=("Microsoft YaHei", 9), fg="#484f58", bg="#0d1117").pack(anchor=tk.W)

    def _browse(self):
        path = filedialog.askdirectory(title="Select Novels Directory")
        if path:
            self.path_var.set(path)

    def _start(self):
        port = int(self.port_var.get())
        save_path = self.path_var.get()

        self.settings = {"save_path": save_path, "port": port}
        save_settings(self.settings)

        self.start_btn.configure(state=tk.DISABLED, text="⏳ Starting...")
        self.stop_btn.configure(state=tk.NORMAL)
        self.open_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text="● Starting", fg="#d29922")

        self._append_log("━━━ Starting Backend ━━━")
        self._append_log(f"Python: {self.python_path}")
        self._append_log(f"Backend: {self.backend_dir}")
        self._append_log(f"Port: {port}")

        self.backend.start(self.python_path, self.backend_dir, port)

        def check():
            import urllib.request
            for i in range(25):
                time.sleep(0.8)
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=2)
                    self.root.after(0, self._on_ready, port)
                    return
                except Exception:
                    self._append_log(f"Waiting... ({i+1}/25)")
            self.root.after(0, self._on_fail)

        threading.Thread(target=check, daemon=True).start()

    def _on_ready(self, port):
        self.start_btn.configure(text="✓ Running", bg="#1a7f37")
        self.open_btn.configure(state=tk.NORMAL)
        self.status_label.configure(text="● Running", fg="#3fb950")
        self._append_log(f"✓ Ready at http://127.0.0.1:{port}")
        # Auto-open browser
        webbrowser.open(f"http://127.0.0.1:{port}")

    def _on_fail(self):
        self.start_btn.configure(text="▶ Start Server", bg="#238636", state=tk.NORMAL)
        self.status_label.configure(text="● Error", fg="#f85149")
        self._append_log("✗ Failed to start. Check the log above.")

    def _stop(self):
        self.backend.stop()
        self.start_btn.configure(text="▶ Start Server", bg="#238636", state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.open_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text="● Stopped", fg="#f85149")

    def _open_browser(self):
        webbrowser.open(f"http://127.0.0.1:{self.port_var.get()}")

    def _clear_log(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _append_log(self, msg):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _poll_log(self):
        try:
            while True:
                kind, msg = self.log_queue.get_nowait()
                if kind == "log":
                    self._append_log(msg)
                elif kind == "status":
                    self._append_log(f"[Status] {msg}")
        except queue.Empty:
            pass
        self.root.after(200, self._poll_log)

    def _on_close(self):
        if self.backend.running:
            if messagebox.askyesno("Exit", "Backend is running. Stop and exit?"):
                self.backend.stop()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = LauncherApp()
        app.run()
    except Exception as e:
        import traceback
        try:
            import tkinter.messagebox as mb
            mb.showerror("Fatal Error", f"{e}\n\n{traceback.format_exc()}")
        except Exception:
            pass
        raise
