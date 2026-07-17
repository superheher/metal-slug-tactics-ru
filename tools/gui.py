#!/usr/bin/env python3
"""Minimal windowed front-end for the Metal Slug Tactics Russian translation.

A small Tkinter window — game-folder field + Browse, an Install button, a progress
bar and a log — that drives the same patch pipeline as install.py in a background
thread. Built with PyInstaller as a windowed (no-console) single exe.

Run with any command-line argument to fall back to the console installer.
"""
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import install as installer

TITLE = "Metal Slug Tactics — русификатор"


def _art(name):
    """Locate a bundled art file both when frozen (_MEIPASS/art) and from source."""
    for p in (paths.res("art", name), os.path.join(paths.ROOT, "packaging", "art", name)):
        if os.path.isfile(p):
            return p
    return None


def _detect_game():
    try:
        return installer.paths.find_game()
    except (SystemExit, Exception):
        return ""


class _QueueWriter:
    """File-like object: routes text writes into a queue for the GUI log."""
    def __init__(self, q):
        self.q = q

    def write(self, s):
        if s:
            self.q.put(("log", s))

    def flush(self):
        pass


class App:
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()
        self.worker = None
        self._imgs = []
        root.title(TITLE)
        root.resizable(False, False)
        self._build()
        self.path_var.set(_detect_game())
        root.after(80, self._poll)
        root.update_idletasks()
        self._center()

    # ---- layout ----
    def _build(self):
        outer = tk.Frame(self.root)
        outer.pack(fill="both", expand=True)

        poster = _art("poster.png")
        if poster:
            try:
                from PIL import Image, ImageTk
                im = Image.open(poster)
                h = 360
                im = im.resize((round(h * im.size[0] / im.size[1]), h), Image.LANCZOS)
                ph = ImageTk.PhotoImage(im)
                self._imgs.append(ph)
                tk.Label(outer, image=ph, borderwidth=0).pack(side="left", fill="y")
            except Exception:
                pass

        right = tk.Frame(outer, padx=16, pady=14)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Русификатор Metal Slug Tactics",
                 font=("Helvetica", 15, "bold")).pack(anchor="w")
        tk.Label(right, text="Добавляет русский язык прямо в игру.",
                 fg="#555").pack(anchor="w", pady=(0, 12))

        tk.Label(right, text="Папка игры:").pack(anchor="w")
        row = tk.Frame(right)
        row.pack(fill="x", pady=(2, 12))
        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(row, textvariable=self.path_var, width=34)
        self.path_entry.pack(side="left", fill="x", expand=True)
        tk.Button(row, text="Обзор…", command=self._browse).pack(side="left", padx=(6, 0))

        self.install_btn = tk.Button(right, text="Установить русский",
                                     command=lambda: self._run(False), height=2)
        self.install_btn.pack(fill="x")

        self.status = tk.StringVar(value="Готово к установке.")
        tk.Label(right, textvariable=self.status, anchor="w").pack(fill="x", pady=(12, 2))
        self.prog = ttk.Progressbar(right, mode="determinate", maximum=4)
        self.prog.pack(fill="x")

        self.log = tk.Text(right, height=8, width=48, state="disabled", wrap="word",
                           bg="#1e1e1e", fg="#dcdcdc", relief="flat", font=("Menlo", 10))
        self.log.pack(fill="both", expand=True, pady=(10, 0))

        bottom = tk.Frame(right)
        bottom.pack(fill="x", pady=(8, 0))
        self.revert_btn = tk.Button(bottom, text="Откат на английский",
                                    command=lambda: self._run(True), relief="flat", fg="#666")
        self.revert_btn.pack(side="left")
        bd = installer._build_date()
        if bd:
            tk.Label(bottom, text=f"build {bd}", fg="#999").pack(side="right")

    def _center(self):
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 3}")

    # ---- actions ----
    def _browse(self):
        d = filedialog.askdirectory(title="Папка игры Metal Slug Tactics")
        if d:
            self.path_var.set(d)

    def _run(self, revert):
        if self.worker and self.worker.is_alive():
            return
        path = self.path_var.get().strip()
        if path:
            os.environ["MST_PATH"] = path
        paths._GAME = None                       # drop the cached lazy paths so a new one resolves
        for a in ("GAME", "AA", "OPTIONS"):      # pop from __dict__ directly (hasattr would
            paths.__dict__.pop(a, None)          # trigger the lazy __getattr__ we are resetting)
        self._set_busy(True)
        self.prog.configure(value=0)
        self.status.set("Откат…" if revert else "Установка…")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.worker = threading.Thread(target=self._work, args=(revert,), daemon=True)
        self.worker.start()

    def _work(self, revert):
        saved = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = _QueueWriter(self.q)
        code = 1
        try:
            code = installer.revert() if revert else installer.install(dry_run=False)
        except SystemExit as e:
            if e.code not in (0, None):
                print(f"\n{e.code}")
            code = e.code if isinstance(e.code, int) else 1
        except Exception as e:
            print(f"\n✗ {e}")
            code = 1
        finally:
            sys.stdout, sys.stderr = saved
            self.q.put(("done", code))

    # ---- gui updates on the main thread ----
    def _set_busy(self, busy):
        st = "disabled" if busy else "normal"
        self.install_btn.configure(state=st)
        self.revert_btn.configure(state=st)

    def _append(self, s):
        self.log.configure(state="normal")
        self.log.insert("end", s)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _poll(self):
        try:
            while True:
                kind, val = self.q.get_nowait()
                if kind == "log":
                    self._append(val)
                    if "══" in val and self.prog["value"] < 4:
                        self.prog.step(1)
                elif kind == "done":
                    self._set_busy(False)
                    ok = val in (0, None)
                    self.prog.configure(value=4 if ok else 0)
                    self.status.set("Готово! Запустите игру." if ok
                                    else "Не получилось — смотрите лог.")
        except queue.Empty:
            pass
        self.root.after(80, self._poll)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:            # any arg -> console installer (dev / power users)
        sys.exit(installer.main())
    main()
