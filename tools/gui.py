#!/usr/bin/env python3
"""Minimal windowed front-end for the Metal Slug Tactics Russian translation.

A small themed window — game-folder field + Browse, an Install button, a progress
bar and a log — that drives the same patch pipeline as install.py in a background
thread. Built with PyInstaller as a windowed (no-console) single exe.

Uses the Sun Valley (sv-ttk) theme when available: native Windows 11 look with a
light/dark variant that follows the system setting. Falls back to plain ttk.

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
INSTALL_PHASES = ["Сохраняю оригиналы игры…", "Проверяю перевод…",
                  "Собираю русские бандлы…", "Устанавливаю в игру…"]


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


def _dark_titlebar(root):
    """Match the Windows title bar to a dark theme (no-op elsewhere)."""
    try:
        import ctypes
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
    except Exception:
        pass


def _app_id():
    """Give the process its own taskbar identity so Windows uses our window icon."""
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("superheher.mst-ru")
    except Exception:
        pass


def _register_mono():
    """Register the bundled JetBrains Mono NL for this process; return the family to use."""
    ttf = _art("JetBrainsMonoNL-Regular.ttf")
    if ttf:
        try:
            import ctypes
            ctypes.windll.gdi32.AddFontResourceExW(ctypes.c_wchar_p(ttf), 0x10, 0)  # FR_PRIVATE
            return "JetBrains Mono NL"
        except Exception:
            pass
    return "TkFixedFont"


class _Tip:
    """Theme-aware hover tooltip, delayed, drawn INSIDE the window just above the widget
    (so it never spills off the screen edge)."""
    def __init__(self, widget, text, dark=False):
        self.widget, self.after_id = widget, None
        self.label = tk.Label(widget.winfo_toplevel(), text=text,
                              background="#2b2b2b" if dark else "#ffffff",
                              foreground="#e6e6e6" if dark else "#1a1a1a",
                              padx=7, pady=4, font=("", 9), relief="solid", borderwidth=1)
        widget.bind("<Enter>", self._enter)
        widget.bind("<Leave>", self._leave)

    def _enter(self, _):
        self.after_id = self.widget.after(1200, self._show)

    def _leave(self, _):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.label.place_forget()

    def _show(self):
        self.after_id = None
        self.label.place(in_=self.widget, relx=1.0, rely=0.0, anchor="se", y=-4)
        self.label.lift()


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
        self._buf = ""
        self._phase = 0
        self._revert = False
        _app_id()
        root.title(TITLE)
        root.resizable(False, False)
        self._set_icon(root)
        self.mono = _register_mono()
        self.dark = self._init_theme()
        self._build()
        self.path_var.set(_detect_game())
        root.after(80, self._poll)
        root.update_idletasks()
        self._center()
        if self.dark:
            _dark_titlebar(root)

    def _set_icon(self, root):
        try:
            from PIL import Image, ImageTk
            png = _art("mst-ru.png")
            if not png:
                return
            im = Image.open(png)
            icons = [ImageTk.PhotoImage(im.resize((s, s), Image.LANCZOS)) for s in (256, 64, 48, 32, 16)]
            self._imgs.extend(icons)
            root.iconphoto(True, *icons)
        except Exception:
            pass

    def _init_theme(self):
        dark = False
        try:
            import darkdetect
            dark = bool(darkdetect.isDark())
        except Exception:
            pass
        try:
            import sv_ttk
            sv_ttk.set_theme("dark" if dark else "light")
        except Exception:
            pass
        return dark

    # ---- layout ----
    def _build(self):
        base = tkfont.nametofont("TkDefaultFont")
        fam, sz = base.cget("family"), base.cget("size")
        title_font = (fam, sz + 5, "bold")
        small_font = (fam, max(8, sz - 1))
        link_fg = "#5a9bff" if self.dark else "#2f6fd0"
        mono = self.mono
        log_font = (mono, 10) if mono != "TkFixedFont" else "TkFixedFont"
        link_font = (mono, max(8, sz - 1)) if mono != "TkFixedFont" else small_font

        ttk.Style(self.root).configure("Big.TButton", padding=(0, 8))

        right = ttk.Frame(self.root, padding=(18, 16))
        right.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right, text="Русификатор Metal Slug Tactics", font=title_font).pack(anchor="w")
        ttk.Label(right, text="Добавляет русский язык прямо в игру.").pack(anchor="w")
        ttk.Label(right, text=f"Заменяет бразильский португальский · для версии игры {GAME_VERSION}"
                  ).pack(anchor="w", pady=(0, 16))

        ttk.Label(right, text="Папка игры:").pack(anchor="w")
        row = ttk.Frame(right)
        row.pack(fill="x", pady=(3, 16))
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(row, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Обзор…", command=self._browse, width=8).pack(side="left", padx=(8, 0))

        self.install_btn = ttk.Button(right, text="Установить русский", style="Big.TButton",
                                      command=lambda: self._run(False))
        self.install_btn.pack(fill="x")

        self.status = tk.StringVar(value="Готово к установке.")
        ttk.Label(right, textvariable=self.status, anchor="w").pack(fill="x", pady=(16, 4))
        self.prog = ttk.Progressbar(right, mode="determinate", maximum=4)
        self.prog.pack(fill="x")

        logf = ttk.Frame(right)
        logf.pack(fill="both", expand=True, pady=(14, 0))
        sb = ttk.Scrollbar(logf)
        sb.pack(side="right", fill="y")
        self.log = tk.Text(logf, height=9, width=52, state="disabled", wrap="char",
                           relief="flat", borderwidth=0, padx=10, pady=8,
                           highlightthickness=1, font=log_font,
                           bg="#1d1d1d" if self.dark else "#fbfbfb",
                           fg="#d6d6d6" if self.dark else "#1a1a1a",
                           highlightbackground="#3a3a3a" if self.dark else "#cccccc",
                           highlightcolor="#3a3a3a" if self.dark else "#cccccc",
                           selectbackground="#38517a" if self.dark else "#cfe0f5",
                           selectforeground="#ffffff" if self.dark else "#000000",
                           yscrollcommand=sb.set)
        self.log.pack(side="left", fill="both", expand=True)
        sb.config(command=self.log.yview)
        self.log.tag_configure("ok", foreground="#4ec96a" if self.dark else "#1a7f37")
        self.log.tag_configure("err", foreground="#ff6b60" if self.dark else "#cf222e")
        self.log.tag_configure("hdr", foreground="#8ab4f8" if self.dark else "#2f6fd0")
        self.log.tag_raise("sel")   # selection colours must win over the coloured tags

        bottom = ttk.Frame(right)
        bottom.pack(fill="x", pady=(12, 0))
        self.revert_btn = ttk.Button(bottom, text="Откат на английский", width=20,
                                     command=lambda: self._run(True))
        self.revert_btn.pack(side="left")
        bd = installer._build_date()
        link = ttk.Label(bottom, text=(f"build {bd}  ↗" if bd else "GitHub  ↗"),
                         foreground=link_fg, cursor="hand2", font=link_font)
        link.pack(side="right")
        link.bind("<ButtonRelease-1>", lambda e: webbrowser.open(REPO_URL))
        _Tip(link, REPO_URL, self.dark)

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
        self._revert = revert
        self._phase = 0
        self._buf = ""
        self._set_busy(True)
        self.prog.configure(value=0)
        self.status.set("Откат на английский…" if revert else "Установка перевода…")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self._append(("Откат на английский…\n" if revert else "Установка перевода…\n"), "hdr")
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

    def _append(self, s, tag=None):
        if tag is None:
            tag = "ok" if "✓" in s else "err" if "✗" in s else "hdr" if "══" in s else ""
        self.log.configure(state="normal")
        self.log.insert("end", s, tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _curate(self, line):
        """Show a short, friendly line instead of the engine's long raw output."""
        if "══" in line:
            i = self._phase
            self._phase += 1
            if self.prog["value"] < 4:
                self.prog.step(1)
            self._append((INSTALL_PHASES[i] if i < len(INSTALL_PHASES)
                          else line.strip("═ ")) + "\n", "hdr")
        elif "✗" in line and line.strip():
            self._append(line.strip() + "\n", "err")
        # verbose per-item lines are dropped on purpose — too long for the narrow log

    def _poll(self):
        try:
            while True:
                kind, val = self.q.get_nowait()
                if kind == "log":
                    self._buf += val
                    while "\n" in self._buf:
                        line, self._buf = self._buf.split("\n", 1)
                        self._curate(line)
                elif kind == "done":
                    self._set_busy(False)
                    ok = val in (0, None)
                    self.prog.configure(value=4 if ok else 0)
                    if ok:
                        self.status.set("Готово. Английский возвращён." if self._revert
                                        else "Готово! Запустите игру.")
                        self._append(("✓ Английский возвращён.\n" if self._revert
                                      else "✓ Готово! Русский включён.\n"), "ok")
                    else:
                        self.status.set("Не получилось — смотрите лог.")
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
