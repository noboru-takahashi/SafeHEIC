import sys
import json
import os
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog

from tkinterdnd2 import DND_FILES, TkinterDnD

from PIL import Image
from pillow_heif import register_heif_opener


APP_NAME = "SafeHEIC"
APP_VERSION = "0.1.0"


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return str(Path(sys._MEIPASS) / relative_path)

    # src/safeheic.py から見て、assets は1階層上
    project_root = Path(__file__).resolve().parent.parent
    return str(project_root / relative_path)


def settings_path() -> Path:
    appdata = os.getenv("APPDATA")

    if appdata:
        base = Path(appdata) / APP_NAME
    else:
        base = Path.home() / ".safeheic"

    base.mkdir(parents=True, exist_ok=True)
    return base / "settings.json"


TEXTS = {
    "en": {
        "title": APP_NAME,
        "subtitle": "Offline HEIC to JPG converter",
        "drop": "Drop HEIC files or folders here",
        "browse_files": "Browse Files",
        "browse_folder": "Browse Folder",
        "clear": "Clear",
        "footer": f"Offline / No upload / Open source / by @noborutkhs / v{APP_VERSION}",
        "status": "Ready",
        "done": "Done",
    },
    "ja": {
        "title": APP_NAME,
        "subtitle": "オフラインでHEICをJPEGに変換",
        "drop": "HEICファイル・フォルダをここにドロップ",
        "browse_files": "ファイル選択",
        "browse_folder": "フォルダ選択",
        "clear": "クリア",
        "footer": f"オフライン / アップロードなし / オープンソース / by @noborutkhs / v{APP_VERSION}",
        "status": "待機中",
        "done": "完了",
    },
}


class SafeHEICConverter:
    def __init__(self):
        register_heif_opener()

        self.root = TkinterDnD.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("760x600")
        self.root.minsize(680, 560)

        self.images = {}
        self.lang = self.load_settings()
        self.ui_font_family = "Yu Gothic UI"

        self.colors = {
            "window_bg": "#F5F7FA",
            "header_bg": "#FFFFFF",
            "drop_bg": "#FFFFFF",
            "drop_border": "#B8C2CC",
            "footer_bg": "#EEF2F6",
            "primary": "#1F6FEB",
            "primary_light": "#DCEBFF",
            "text": "#1F2933",
            "muted": "#6B7280",
            "button_bg": "#FFFFFF",
            "button_border": "#C9D1D9",
            "button_active": "#EEF2F6",
            "inactive_bg": "#FFFFFF",
            "active_bg": "#DCEBFF",
        }

        self.load_images()
        self.setup_style()
        self.build_ui()
        self.register_dnd()
        self.update_language()
        self.set_window_icon()

    def font(self, size: int, weight: str = "normal"):
        return (self.ui_font_family, size, weight)

    def set_window_icon(self):
        icon_path = resource_path("assets/icon.png")

        try:
            icon_image = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon_image)
            self.window_icon = icon_image
        except Exception:
            pass

    def load_settings(self) -> str:
        path = settings_path()

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            lang = data.get("lang", "en")
            return lang if lang in TEXTS else "en"
        except Exception:
            return "en"

    def save_settings(self):
        path = settings_path()
        data = {"lang": self.lang}

        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_images(self):
        image_files = {
            "logo": "assets/logo.png",
            "drop": "assets/drop.png",
            "file": "assets/file.png",
            "folder": "assets/folder.png",
            "flag_us": "assets/flag_us.png",
            "flag_jp": "assets/flag_jp.png",
        }

        for key, rel_path in image_files.items():
            path = resource_path(rel_path)

            try:
                img = tk.PhotoImage(file=path)

                if key in ("flag_us", "flag_jp"):
                    img = img.subsample(2, 2)

                self.images[key] = img
            except Exception:
                self.images[key] = None

    def setup_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.root.configure(bg=self.colors["window_bg"])

        self.style.configure("App.TFrame", background=self.colors["window_bg"])
        self.style.configure("Header.TFrame", background=self.colors["header_bg"])
        self.style.configure("Footer.TFrame", background=self.colors["footer_bg"])

        self.style.configure(
            "Title.TLabel",
            background=self.colors["header_bg"],
            foreground=self.colors["text"],
            font=self.font(22, "bold"),
        )

        self.style.configure(
            "Subtitle.TLabel",
            background=self.colors["header_bg"],
            foreground=self.colors["muted"],
            font=self.font(10),
        )

        self.style.configure(
            "Drop.TLabel",
            background=self.colors["drop_bg"],
            foreground=self.colors["text"],
            font=self.font(15, "bold"),
        )

        self.style.configure(
            "Footer.TLabel",
            background=self.colors["footer_bg"],
            foreground=self.colors["muted"],
            font=self.font(9),
        )

    def build_ui(self):
        self.main = ttk.Frame(self.root, style="App.TFrame")
        self.main.pack(fill="both", expand=True)

        self.header = ttk.Frame(
            self.main,
            style="Header.TFrame",
            padding=(24, 20),
        )
        self.header.pack(fill="x")

        self.header_left = ttk.Frame(self.header, style="Header.TFrame")
        self.header_left.pack(side="left", fill="x", expand=True)

        if self.images["logo"]:
            self.logo_label = ttk.Label(
                self.header_left,
                image=self.images["logo"],
                background=self.colors["header_bg"],
            )
            self.logo_label.pack(side="left", padx=(0, 14))

        self.title_block = ttk.Frame(self.header_left, style="Header.TFrame")
        self.title_block.pack(side="left", fill="x", expand=True)

        self.title_label = ttk.Label(self.title_block, style="Title.TLabel")
        self.title_label.pack(anchor="w")

        self.subtitle_label = ttk.Label(self.title_block, style="Subtitle.TLabel")
        self.subtitle_label.pack(anchor="w", pady=(4, 0))

        self.language_switch = tk.Frame(
            self.header,
            bg=self.colors["header_bg"],
            highlightthickness=1,
            highlightbackground=self.colors["button_border"],
        )
        self.language_switch.pack(side="right")

        self.lang_en_button = self.create_language_segment(
            parent=self.language_switch,
            lang="en",
            image=self.images["flag_us"],
        )
        self.lang_en_button.pack(side="left")

        self.lang_ja_button = self.create_language_segment(
            parent=self.language_switch,
            lang="ja",
            image=self.images["flag_jp"],
        )
        self.lang_ja_button.pack(side="left")

        self.body = ttk.Frame(
            self.main,
            style="App.TFrame",
            padding=(24, 20),
        )
        self.body.pack(fill="both", expand=True)

        self.drop_area = tk.Frame(
            self.body,
            bg=self.colors["drop_bg"],
            highlightbackground=self.colors["drop_border"],
            highlightthickness=2,
            bd=0,
        )
        self.drop_area.pack(fill="both", expand=True)

        self.drop_inner = tk.Frame(self.drop_area, bg=self.colors["drop_bg"])
        self.drop_inner.pack(fill="both", expand=True, padx=24, pady=16)

        if self.images["drop"]:
            self.drop_icon_label = tk.Label(
                self.drop_inner,
                image=self.images["drop"],
                bg=self.colors["drop_bg"],
            )
            self.drop_icon_label.pack(pady=(0, 8))

        self.drop_label = ttk.Label(self.drop_inner, style="Drop.TLabel")
        self.drop_label.pack(pady=(0, 10))

        self.path_list = tk.Listbox(
            self.drop_inner,
            font=self.font(10),
            height=5,
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#D0D7DE",
            selectbackground=self.colors["primary"],
        )
        self.path_list.pack(fill="x", expand=False, pady=(0, 14))

        self.button_row = tk.Frame(self.drop_inner, bg=self.colors["drop_bg"])
        self.button_row.pack(side="bottom", fill="x", pady=(0, 0))

        self.file_button = self.create_icon_button(
            parent=self.button_row,
            text=TEXTS[self.lang]["browse_files"],
            image=self.images["file"],
            command=self.browse_files,
        )
        self.file_button.pack(side="left")

        self.folder_button = self.create_icon_button(
            parent=self.button_row,
            text=TEXTS[self.lang]["browse_folder"],
            image=self.images["folder"],
            command=self.browse_folder,
        )
        self.folder_button.pack(side="left", padx=(10, 0))

        self.clear_button = self.create_icon_button(
            parent=self.button_row,
            text=TEXTS[self.lang]["clear"],
            image=None,
            command=self.clear_list,
        )
        self.clear_button.pack(side="right")

        self.footer = ttk.Frame(
            self.main,
            style="Footer.TFrame",
            padding=(24, 10),
        )
        self.footer.pack(fill="x")

        self.status_var = tk.StringVar()

        self.status_label = ttk.Label(
            self.footer,
            textvariable=self.status_var,
            style="Footer.TLabel",
        )
        self.status_label.pack(side="left")

        self.footer_label = ttk.Label(self.footer, style="Footer.TLabel")
        self.footer_label.pack(side="right")

    def create_language_segment(self, parent, lang, image):
        segment = tk.Frame(
            parent,
            bg=self.colors["inactive_bg"],
            cursor="hand2",
            padx=10,
            pady=8,
        )

        inner = tk.Frame(segment, bg=self.colors["inactive_bg"], cursor="hand2")
        inner.pack()

        icon = None

        if image:
            icon = tk.Label(
                inner,
                image=image,
                bg=self.colors["inactive_bg"],
                cursor="hand2",
            )
            icon.pack()
            segment.icon_label = icon

        segment.inner = inner
        segment.lang = lang

        def on_click(_):
            self.set_language(lang)

        for widget in (segment, inner):
            widget.bind("<Button-1>", on_click)

        if icon:
            icon.bind("<Button-1>", on_click)

        return segment

    def update_language_segments(self):
        for segment in (self.lang_en_button, self.lang_ja_button):
            is_active = segment.lang == self.lang
            bg = self.colors["active_bg"] if is_active else self.colors["inactive_bg"]

            segment.configure(bg=bg)
            segment.inner.configure(bg=bg)

            if hasattr(segment, "icon_label"):
                segment.icon_label.configure(bg=bg)

    def create_icon_button(self, parent, text, image, command):
        button = tk.Frame(
            parent,
            bg=self.colors["button_bg"],
            highlightthickness=1,
            highlightbackground=self.colors["button_border"],
            highlightcolor=self.colors["button_border"],
            cursor="hand2",
        )

        inner = tk.Frame(button, bg=self.colors["button_bg"], cursor="hand2")
        inner.pack(padx=12, pady=8)

        icon = None

        if image:
            icon = tk.Label(
                inner,
                image=image,
                bg=self.colors["button_bg"],
                cursor="hand2",
            )
            icon.pack(side="left", padx=(0, 8))
            button.icon_label = icon

        label = tk.Label(
            inner,
            text=text,
            font=self.font(10),
            bg=self.colors["button_bg"],
            fg=self.colors["text"],
            cursor="hand2",
        )
        label.pack(side="left")
        button.text_label = label

        def set_bg(color):
            button.configure(bg=color)
            inner.configure(bg=color)
            label.configure(bg=color)

            if icon:
                icon.configure(bg=color)

        def on_enter(_):
            set_bg(self.colors["button_active"])

        def on_leave(_):
            set_bg(self.colors["button_bg"])

        def on_click(_):
            command()

        widgets = [button, inner, label]

        if icon:
            widgets.append(icon)

        for widget in widgets:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return button

    def register_dnd(self):
        for widget in (
            self.root,
            self.main,
            self.body,
            self.drop_area,
            self.drop_inner,
            self.path_list,
        ):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self.on_drop)

    def parse_drop_files(self, data: str) -> list[str]:
        return list(self.root.tk.splitlist(data))

    def make_output_path(self, input_path: Path) -> Path:
        output_path = input_path.with_suffix(".jpg")

        if not output_path.exists():
            return output_path

        counter = 1

        while True:
            candidate = input_path.with_name(f"{input_path.stem}_{counter}.jpg")

            if not candidate.exists():
                return candidate

            counter += 1

    def convert_heic_file(self, file_path: str):
        try:
            input_path = Path(file_path)

            if input_path.suffix.lower() != ".heic":
                return

            output_path = self.make_output_path(input_path)

            image = Image.open(input_path)
            image = image.convert("RGB")
            image.save(output_path, "JPEG", quality=95)

            self.path_list.insert(
                "end",
                f"[OK] {input_path.name} -> {output_path.name}",
            )

        except Exception as e:
            self.path_list.insert(
                "end",
                f"[ERR] {Path(file_path).name} : {e}",
            )

    def add_paths(self, paths: list[str]):
        for path in paths:
            p = Path(path)

            if p.is_dir():
                files = [
                    f for f in p.iterdir()
                    if f.is_file() and f.suffix.lower() == ".heic"
                ]

                for file in files:
                    self.convert_heic_file(str(file))
            else:
                self.convert_heic_file(str(p))

        self.status_var.set(TEXTS[self.lang]["done"])

    def on_drop(self, event):
        paths = self.parse_drop_files(event.data)
        self.add_paths(paths)

    def browse_files(self):
        paths = filedialog.askopenfilenames(
            title="Select HEIC files",
            filetypes=[
                ("HEIC files", "*.heic *.HEIC"),
                ("All files", "*.*"),
            ],
        )

        self.add_paths(list(paths))

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select folder")

        if folder:
            self.add_paths([folder])

    def clear_list(self):
        self.path_list.delete(0, "end")
        self.status_var.set(TEXTS[self.lang]["status"])

    def set_language(self, lang):
        if lang == self.lang:
            return

        self.lang = lang
        self.save_settings()
        self.update_language()

    def update_language(self):
        t = TEXTS[self.lang]

        self.title_label.configure(text=t["title"])
        self.subtitle_label.configure(text=t["subtitle"])
        self.drop_label.configure(text=t["drop"])
        self.footer_label.configure(text=t["footer"])

        self.file_button.text_label.configure(text=t["browse_files"])
        self.folder_button.text_label.configure(text=t["browse_folder"])
        self.clear_button.text_label.configure(text=t["clear"])

        self.update_language_segments()

        if self.path_list.size() == 0:
            self.status_var.set(t["status"])

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SafeHEICConverter()
    app.run()
    