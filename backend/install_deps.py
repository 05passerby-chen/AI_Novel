# backend/install_deps.py
# -*- coding: utf-8 -*-
"""
AI Novel Editor — Dependency Installer EXE

This tool:
1. Detects Python installation
2. Installs required pip packages
3. Creates .env file with paths

After running this, the user can run launcher.exe
"""
import sys
import os
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# ─── Paths (handle both source and PyInstaller frozen) ─────────────
if getattr(sys, 'frozen', False):
    _EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    _EXE_DIR = os.path.dirname(os.path.abspath(__file__))

# The backend directory — try exe dir first (source run from backend/),
# then exe_dir/backend (exe placed at project root)
if os.path.exists(os.path.join(_EXE_DIR, "requirements.txt")):
    ROOT = _EXE_DIR
else:
    ROOT = os.path.join(_EXE_DIR, "backend")

REQUIREMENTS = os.path.join(ROOT, "requirements.txt")
ENV_FILE = os.path.join(ROOT, ".env")


class InstallerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Novel Editor — Install Dependencies")
        self.root.geometry("620x480")
        self.root.configure(bg="#0d1117")
        self.root.minsize(500, 380)
        try:
            icon = os.path.join(os.path.dirname(ROOT), "icon.ico")
            if os.path.exists(icon):
                self.root.iconbitmap(icon)
        except Exception:
            pass

        self.python_path = ""
        self._build_ui()
        self.root.after(400, self._safe_run)

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#0d1117")
        header.pack(fill=tk.X, padx=20, pady=(20, 6))
        tk.Label(header, text="📦 AI Novel Editor — Dependency Installer",
                 font=("Microsoft YaHei", 14, "bold"), fg="#e6edf3", bg="#0d1117").pack(anchor=tk.W)
        tk.Label(header, text="This will install all required packages for the novel editor.",
                 font=("Microsoft YaHei", 10), fg="#8b949e", bg="#0d1117").pack(anchor=tk.W, pady=(4, 0))

        # Progress
        self.progress = ttk.Progressbar(self.root, mode="indeterminate", length=580)
        self.progress.pack(padx=20, pady=(12, 8))

        self.status_label = tk.Label(self.root, text="Detecting Python...", font=("Microsoft YaHei", 10),
                                      fg="#d29922", bg="#0d1117")
        self.status_label.pack(anchor=tk.W, padx=20)

        # Log
        log_frame = tk.Frame(self.root, bg="#0d1117")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(8, 12))
        self.log_text = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, font=("Consolas", 9),
            bg="#161b22", fg="#c9d1d9", relief=tk.FLAT,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)

        # Button (hidden until done)
        self.btn_frame = tk.Frame(self.root, bg="#0d1117")
        self.btn_frame.pack(fill=tk.X, padx=20, pady=(0, 16))

    def _log(self, msg):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.root.update()

    def _safe_run(self):
        try:
            self._run()
        except Exception as e:
            import traceback
            self._log(f"\n✗ Unexpected error: {e}")
            self._log(traceback.format_exc())
            self._finish(False, f"Error: {e}")

    def _run(self):
        self.progress.start(8)

        # Step 1: Detect Python
        self._log("━━━ Step 1: Detecting Python ━━━")
        python = self._find_python()
        if not python:
            self._finish(False, "Python not found. Please install Python 3.9+ from python.org")
            return
        self.python_path = python
        self._log(f"✓ Found: {python}")
        self._log(f"  Version: {sys.version.split()[0]}")

        # Step 2: Install packages
        self._log("\n━━━ Step 2: Installing Packages ━━━")
        self.status_label.configure(text="Installing packages...")
        if not os.path.exists(REQUIREMENTS):
            self._finish(False, f"requirements.txt not found at {REQUIREMENTS}")
            return

        ok = self._pip_install()
        if not ok:
            self._finish(False, "Package installation failed")
            return

        # Step 3: Write .env
        self._log("\n━━━ Step 3: Writing .env ━━━")
        self._write_env()
        self._log(f"✓ .env written to {ENV_FILE}")

        # Step 4: Verify
        self._log("\n━━━ Step 4: Verifying ━━━")
        self._verify()
        self._log("✓ All checks passed!")

        self._finish(True, "All dependencies installed. You can now run launcher.exe")

    def _find_python(self) -> str:
        """Find a working Python 3.9+ installation."""
        candidates = ["python", "python3", "py"]

        for cmd in candidates:
            try:
                result = subprocess.run(
                    [cmd, "--version"], capture_output=True, text=True, timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
                if result.returncode == 0:
                    ver = result.stdout.strip()
                    self._log(f"  Trying {cmd}: {ver}")
                    # Check version >= 3.9
                    parts = ver.replace("Python ", "").split(".")
                    if int(parts[0]) >= 3 and int(parts[1]) >= 9:
                        return cmd
            except Exception:
                pass

        # Check common install paths on Windows
        common_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python311\python.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python312\python.exe"),
            r"C:\Python311\python.exe",
            r"C:\Python312\python.exe",
            os.path.expandvars(r"%ProgramFiles%\Python311\python.exe"),
        ]
        for p in common_paths:
            if os.path.exists(p):
                self._log(f"  Found at: {p}")
                return p

        return ""

    def _pip_install(self) -> bool:
        try:
            result = subprocess.run(
                [self.python_path, "-m", "pip", "install", "-r", REQUIREMENTS],
                capture_output=True, text=True, timeout=600,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            for line in result.stdout.split("\n"):
                if line.strip():
                    self._log(f"  {line.strip()}")
            if result.stderr:
                for line in result.stderr.split("\n"):
                    if line.strip() and ("ERROR" in line or "WARNING" in line):
                        self._log(f"  {line.strip()}")
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            self._log("  ✗ Timed out (>10 min). Check network.")
            return False
        except Exception as e:
            self._log(f"  ✗ Error: {e}")
            return False

    def _write_env(self):
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(f"# AI Novel Editor — Environment\n")
            f.write(f"PYTHON_PATH={self.python_path}\n")
            f.write(f"BACKEND_DIR={ROOT}\n")
            f.write(f"PORT=8765\n")
            f.write(f"NOVELS_DIR={os.path.expanduser('~/Novels')}\n")

    def _verify(self):
        """Quick verification that key packages are importable."""
        try:
            result = subprocess.run(
                [self.python_path, "-c", "import fastapi, uvicorn, openai, chromadb, pydantic; print('OK')"],
                capture_output=True, text=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            self._log(f"  Import test: {result.stdout.strip()}")
        except Exception as e:
            self._log(f"  Warning: {e}")

    def _finish(self, success: bool, msg: str):
        self.progress.stop()
        if success:
            self.status_label.configure(text=f"✓ {msg}", fg="#3fb950")
        else:
            self.status_label.configure(text=f"✗ {msg}", fg="#f85149")

        # Add close button
        tk.Button(self.btn_frame, text="Close", font=("Microsoft YaHei", 10, "bold"),
                  bg="#238636" if success else "#da3633", fg="#fff", relief=tk.FLAT,
                  command=self.root.destroy, cursor="hand2",
                  activebackground="#2ea043", activeforeground="#fff",
                  ).pack(side=tk.RIGHT, ipadx=20, ipady=6)
        self.root.update()


if __name__ == "__main__":
    try:
        app = InstallerApp()
        app.root.mainloop()
    except Exception as e:
        import traceback
        # Last-resort fallback: show error in a popup if GUI is alive
        try:
            import tkinter.messagebox as mb
            mb.showerror("Fatal Error", f"{e}\n\n{traceback.format_exc()}")
        except Exception:
            pass
        raise
