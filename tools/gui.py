#!/usr/bin/env python3
"""Minimal windowed front-end for the Metal Slug Tactics Russian translation.

A small themed (ttk) Tkinter window — game-folder field + Browse, an Install button,
a progress bar and a log — that drives the same patch pipeline as install.py in a
background thread. Built with PyInstaller as a windowed (no-console) single exe.
On Windows the ttk widgets render with the native visual style (Segoe UI, real buttons).

Run with any command-line argument to fall back to the console installer.
"""
import os
import queue
import sys
import threading
import webbrowser
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import install as installer

TITLE = "Metal Slug Tactics — русификатор"
REPO_URL = "https://github.com/superheher/metal-slug-tactics-ru"
GAME_VERSION = "1.0.4"


class _Null:
    """A windowed PyInstaller build has sys.stdout/stderr = None; keep stray prints harmless."""
    def write(self, *_):
        pass

    def flush(self):
        pass


for _s in ("stdout", "stderr"):
    if getattr(sys, _s) is None:
        setattr(sys, _s, _Null())


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
        try:
            ico = _art("mst-ru.ico")
            if ico:
                root.iconbitmap(ico)
        except Exception:
            pass
        self._build()
        self.path_var.set(_detect_game())
        root.after(80, self._poll)
        root.update_idletasks()
        self._center()

    # ---- layout ----
    def _build(self):
        base = tkfont.nametofont("TkDefaultFont")
        fam, sz = base.cget("family"), base.cget("size")
        title_font = (fam, sz + 5, "bold")
        small_font = (fam, max(8, sz - 1))

        ttk.Style(self.root).configure("Big.TButton", padding=(0, 7))

        right = ttk.Frame(self.root, padding=(16, 14))
        right.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right, text="Русификатор Metal Slug Tactics", font=title_font).pack(anchor="w")
        ttk.Label(right, text="Добавляет русский язык прямо в игру.",
                  foreground="#555").pack(anchor="w")
        ttk.Label(right, foreground="#888", font=small_font,
                  text=f"Русский заменяет бразильский португальский · для версии игры {GAME_VERSION}"
                  ).pack(anchor="w", pady=(2, 14))

        ttk.Label(right, text="Папка игры:").pack(anchor="w")
        row = ttk.Frame(right)
        row.pack(fill="x", pady=(2, 14))
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(row, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Обзор…", command=self._browse, width=8).pack(side="left", padx=(6, 0))

        self.install_btn = ttk.Button(right, text="Установить русский", style="Big.TButton",
                                      command=lambda: self._run(False))
        self.install_btn.pack(fill="x")

        self.status = tk.StringVar(value="Готово к установке.")
        ttk.Label(right, textvariable=self.status, anchor="w").pack(fill="x", pady=(14, 3))
        self.prog = ttk.Progressbar(right, mode="determinate", maximum=4)
        self.prog.pack(fill="x")

        logf = ttk.Frame(right)
        logf.pack(fill="both", expand=True, pady=(12, 0))
        sb = ttk.Scrollbar(logf)
        sb.pack(side="right", fill="y")
        self.log = tk.Text(logf, height=8, width=46, state="disabled", wrap="word",
                           relief="solid", borderwidth=1, padx=6, pady=4,
                           font="TkFixedFont", yscrollcommand=sb.set)
        self.log.pack(side="left", fill="both", expand=True)
        sb.config(command=self.log.yview)

        bottom = ttk.Frame(right)
        bottom.pack(fill="x", pady=(10, 0))
        self.revert_btn = ttk.Button(bottom, text="Откат на английский", width=20,
                                     command=lambda: self._run(True))
        self.revert_btn.pack(side="left")
        bd = installer._build_date()
        link = ttk.Label(bottom, text=(f"build {bd}" if bd else "GitHub"),
                         foreground="#3a6ea5", cursor="hand2", font=small_font)
        link.pack(side="right", pady=(6, 0))
        link.bind("<Button-1>", lambda e: webbrowser.open(REPO_URL))

        # scale the poster to the exact height of the controls -> no empty margins
        self.root.update_idletasks()
        h = right.winfo_reqheight()
        poster = _art("poster.png")
        if poster:
            try:
                from PIL import Image, ImageTk
                im = Image.open(poster)
                ph = ImageTk.PhotoImage(im.resize((round(h * im.size[0] / im.size[1]), h), Image.LANCZOS))
                self._imgs.append(ph)
                ttk.Label(self.root, image=ph, borderwidth=0).grid(row=0, column=0, sticky="ns")
            except Exception:
                pass

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
