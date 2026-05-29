import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from tkcalendar import DateEntry
from main import DocumentProtectionSystem

# ─────────────────────────── Animated Notebook ───────────────────────────────

class AnimatedNotebook(tk.Frame):
    """
    Custom notebook with smooth fade-in animation on tab switch.
    Replaces ttk.Notebook to enable canvas-level animation.
    """

    ANIM_STEPS   = 8      # frames
    ANIM_DELAY   = 18     # ms between frames

    def __init__(self, parent, colors, **kwargs):
        super().__init__(parent, bg=colors["bg_primary"], **kwargs)
        self.colors   = colors
        self._tabs    = []          # list of (title, frame)
        self._current = 0
        self._alpha   = 1.0
        self._anim_id = None

        # ── tab bar ──────────────────────────────────────────────────────────
        self._bar = tk.Frame(self, bg=colors["bg_primary"])
        self._bar.pack(side="top", fill="x")

        # thin accent line under the bar
        self._accent = tk.Frame(self, bg=colors["border"], height=1)
        self._accent.pack(side="top", fill="x")

        # ── content area ─────────────────────────────────────────────────────
        self._content = tk.Frame(self, bg=colors["bg_primary"])
        self._content.pack(side="top", fill="both", expand=True)

    # ── public API ───────────────────────────────────────────────────────────

    def add(self, frame, text: str):
        idx = len(self._tabs)
        self._tabs.append((text, frame))

        btn = tk.Button(
            self._bar,
            text=text,
            bd=0, relief="flat", cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg_primary"],
            fg=self.colors["text_secondary"],
            activebackground=self.colors["bg_secondary"],
            activeforeground=self.colors["primary"],
            padx=20, pady=10,
            command=lambda i=idx: self._select(i),
        )
        btn.pack(side="left")

        frame.place(in_=self._content, x=0, y=0, relwidth=1, relheight=1)
        frame.lower()

        if idx == 0:
            self._show_tab(0, animate=False)

    def select(self, idx: int):
        self._select(idx)

    # ── internals ────────────────────────────────────────────────────────────

    def _select(self, idx: int):
        if idx == self._current:
            return
        if self._anim_id:
            self.after_cancel(self._anim_id)
        self._fade_out(idx)

    def _fade_out(self, next_idx: int):
        """Simulate fade by quickly hiding current and revealing next."""
        # Because vanilla tk has no real alpha on frames we use a fast
        # overlay canvas trick: cover → switch → uncover.
        current_frame = self._tabs[self._current][1]
        overlay = tk.Frame(self._content, bg=self.colors["bg_primary"])
        overlay.place(in_=self._content, x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()

        def step(n, overlay=overlay):
            if n >= self.ANIM_STEPS:
                overlay.destroy()
                return
            # gradually make overlay transparent by scheduling reveal
            self._anim_id = self.after(
                self.ANIM_DELAY,
                lambda: step(n + 1)
            )

        # switch immediately under overlay
        self._show_tab(next_idx, animate=False)
        # then animate overlay away
        step(0)

    def _show_tab(self, idx: int, animate: bool = True):
        self._current = idx
        _, frame = self._tabs[idx]
        frame.lift()
        self._update_tab_bar()

    def _update_tab_bar(self):
        for i, btn in enumerate(self._bar.winfo_children()):
            if not isinstance(btn, tk.Button):
                continue
            if i == self._current:
                btn.config(
                    fg=self.colors["primary"],
                    bg=self.colors["bg_primary"],
                    font=("Segoe UI", 10, "bold"),
                )
                # draw bottom border on active tab via a tiny frame
                # (we use relief trick inside button)
                btn.config(relief="groove", bd=0,
                           highlightthickness=2,
                           highlightcolor=self.colors["primary"],
                           highlightbackground=self.colors["primary"])
            else:
                btn.config(
                    fg=self.colors["text_secondary"],
                    bg=self.colors["bg_primary"],
                    font=("Segoe UI", 10),
                    relief="flat", bd=0,
                    highlightthickness=0,
                )


# ─────────────────────────── Rounded helpers ─────────────────────────────────

def rounded_button(parent, text, command, bg, fg="white",
                   hover_bg=None, font=("Segoe UI", 10, "bold"),
                   padx=18, pady=8, radius=8, width=None):
    """
    A tk.Button styled to appear rounded via consistent padding + relief.
    Tkinter doesn't support real border-radius, so we approximate with
    flat styling + a canvas-drawn rounded rectangle background for key
    action buttons.
    """
    hover_bg = hover_bg or bg
    btn = tk.Button(
        parent,
        text=text, command=command,
        bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
        font=font, relief="flat", bd=0, cursor="hand2",
        padx=padx, pady=pady,
    )
    if width:
        btn.config(width=width)

    def on_enter(e):
        btn.config(bg=hover_bg)

    def on_leave(e):
        btn.config(bg=bg)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def styled_entry(parent, textvariable=None, state="normal",
                 font=("Segoe UI", 10), colors=None, width=None):
    """ttk.Entry with consistent styling."""
    kw = dict(font=font, state=state)
    if textvariable:
        kw["textvariable"] = textvariable
    if width:
        kw["width"] = width
    e = ttk.Entry(parent, **kw)
    return e


def styled_combobox(parent, values, textvariable=None,
                    font=("Segoe UI", 10), width=None):
    kw = dict(values=values, state="readonly", font=font)
    if textvariable:
        kw["textvariable"] = textvariable
    if width:
        kw["width"] = width
    return ttk.Combobox(parent, **kw)


# ─────────────────────────── Main Application ────────────────────────────────

class ProtectionApp:
    # ── field label column width (characters) ──
    LABEL_WIDTH = 30

    def __init__(self, root):
        self.root = root
        self.root.title("Система захисту PDF документів")
        self.root.geometry("980x720")
        self.root.minsize(860, 620)

        self.colors = {
            "bg_primary":    "#FFFFFF",
            "bg_secondary":  "#F5F7FA",
            "bg_tertiary":   "#EEF2F7",
            "primary":       "#2563EB",
            "primary_hover": "#1D4ED8",
            "success":       "#10B981",
            "success_hover": "#059669",
            "danger":        "#EF4444",
            "danger_hover":  "#DC2626",
            "warning":       "#F59E0B",
            "warning_hover": "#D97706",
            "text_primary":  "#1F2937",
            "text_secondary":"#6B7280",
            "text_tertiary": "#9CA3AF",
            "border":        "#E5E7EB",
        }

        self.system = DocumentProtectionSystem()
        self.system.create_dummy_assets()
        self.bg_template_path = os.path.join("png", "background_template.png")

        self._configure_styles()
        self.root.configure(bg=self.colors["bg_primary"])
        self._build_ui()

    # ─────────────────── styles ──────────────────────────────────────────────

    def _configure_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        c = self.colors

        s.configure("TFrame",
                    background=c["bg_primary"], relief="flat", borderwidth=0)
        s.configure("TLabel",
                    background=c["bg_primary"],
                    foreground=c["text_primary"],
                    font=("Segoe UI", 10))
        s.configure("Small.TLabel",
                    font=("Segoe UI", 9),
                    foreground=c["text_secondary"],
                    background=c["bg_primary"])
        s.configure("Header.TLabel",
                    font=("Segoe UI", 16, "bold"),
                    foreground=c["text_primary"],
                    background=c["bg_primary"])
        s.configure("Sub.TLabel",
                    font=("Segoe UI", 11, "bold"),
                    foreground=c["text_primary"],
                    background=c["bg_primary"])

        # Entries
        s.configure("TEntry",
                    font=("Segoe UI", 10),
                    fieldbackground=c["bg_primary"],
                    foreground=c["text_primary"],
                    borderwidth=1,
                    relief="solid",
                    padding=6,
                    lightcolor=c["border"],
                    darkcolor=c["border"])
        s.map("TEntry",
              fieldbackground=[("focus", c["bg_secondary"])],
              lightcolor=[("focus", c["primary"])],
              darkcolor=[("focus", c["primary"])])

        # Combobox
        s.configure("TCombobox",
                    font=("Segoe UI", 10),
                    fieldbackground=c["bg_primary"],
                    foreground=c["text_primary"],
                    borderwidth=1,
                    relief="solid",
                    padding=6,
                    arrowcolor=c["primary"],
                    lightcolor=c["border"],
                    darkcolor=c["border"])
        s.map("TCombobox",
              fieldbackground=[("focus", c["bg_secondary"])])

        # Progressbar
        s.configure("TProgressbar",
                    background=c["success"],
                    troughcolor=c["bg_secondary"],
                    borderwidth=0,
                    thickness=6)

        # Radiobutton
        s.configure("TRadiobutton",
                    background=c["bg_primary"],
                    foreground=c["text_primary"],
                    font=("Segoe UI", 10))
        s.map("TRadiobutton",
              background=[("active", c["bg_primary"])])

        # Scrollbar
        s.configure("TScrollbar",
                    background=c["bg_secondary"],
                    troughcolor=c["bg_primary"],
                    borderwidth=0,
                    arrowcolor=c["text_secondary"])

    # ─────────────────── layout ──────────────────────────────────────────────

    def _build_ui(self):
        c = self.colors

        # ── header ───────────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=c["bg_primary"])
        hdr.pack(fill="x", padx=28, pady=(16, 4))

        tk.Label(hdr, text="🔐  Система захисту PDF документів",
                 bg=c["bg_primary"], fg=c["text_primary"],
                 font=("Segoe UI", 16, "bold")).pack(side="left")

        tk.Frame(self.root, bg=c["border"], height=1).pack(fill="x")

        # ── animated notebook ────────────────────────────────────────────────
        self.notebook = AnimatedNotebook(self.root, c)
        self.notebook.pack(fill="both", expand=True)

        # ── pages ────────────────────────────────────────────────────────────
        self.gen_frame  = tk.Frame(self.notebook, bg=c["bg_primary"])
        self.ver_frame  = tk.Frame(self.notebook, bg=c["bg_primary"])
        self.mass_frame = tk.Frame(self.notebook, bg=c["bg_primary"])

        self.notebook.add(self.gen_frame,  text="  📝  ГЕНЕРУВАННЯ  ")
        self.notebook.add(self.ver_frame,  text="  🔍  ПЕРЕВІРКА  ")
        self.notebook.add(self.mass_frame, text="  📦  МАСОВЕ ГЕНЕРУВАННЯ  ")

        self._build_generate_tab()
        self._build_verify_tab()
        self._build_mass_tab()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — GENERATE
    # ══════════════════════════════════════════════════════════════════════════

    def _build_generate_tab(self):
        """
        Layout: two equal panes side-by-side.
          LEFT  – template selector + dynamic fields (no scroll, grid-based)
          RIGHT – signature + action buttons
        No scrollbar: all elements must fit in full-screen mode.
        """
        c = self.colors
        root_frame = tk.Frame(self.gen_frame, bg=c["bg_primary"])
        root_frame.pack(fill="both", expand=True, padx=24, pady=16)

        # ── LEFT pane ────────────────────────────────────────────────────────
        left = tk.Frame(root_frame, bg=c["bg_primary"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        # Template selector
        self._section_label(left, "📋  Шаблон документа")
        self.template_var = tk.StringVar(value="Cyberverse Certificate")
        templates = [
            "Cyberverse Certificate",
            "Cyberverse Participation Certificate",
            "Certificate of Achievement",
            "Application Form",
            "Contract for Education",
        ]
        cb = styled_combobox(left, templates, textvariable=self.template_var)
        cb.pack(fill="x", pady=(4, 14))
        cb.bind("<<ComboboxSelected>>", self.on_template_change)

        # Divider
        tk.Frame(left, bg=c["border"], height=1).pack(fill="x", pady=(0, 12))

        # Fields section label
        self._section_label(left, "📝  Персональні дані")

        # Fields container – uses grid for consistent alignment
        self.fields_container = tk.Frame(left, bg=c["bg_primary"])
        self.fields_container.pack(fill="both", expand=True, pady=(6, 0))
        self.fields_container.columnconfigure(1, weight=1)

        self.fields        = {}
        self.course_data   = {
            "Introduction to Cybersecurity":           {"platform": "Cisco",    "hours": "15",  "level": "Beginner"},
            "Cybersecurity Essentials":                {"platform": "Cisco",    "hours": "30",  "level": "Intermediate"},
            "Network Security":                        {"platform": "Cisco",    "hours": "40",  "level": "Advanced"},
            "Ethical Hacking (Cisco NetAcad)":         {"platform": "Cisco",    "hours": "70",  "level": "Advanced"},
            "Google Cybersecurity Professional Certificate": {"platform": "Coursera", "hours": "180", "level": "Professional"},
            "IBM Cybersecurity Analyst":               {"platform": "Coursera", "hours": "120", "level": "Intermediate"},
            "Cybersecurity Specialization (Maryland)": {"platform": "Coursera", "hours": "90",  "level": "Advanced"},
            "Applied Cryptography":                    {"platform": "Coursera", "hours": "45",  "level": "Advanced"},
        }
        self.signature_path = ""
        self.last_generated_pdf = ""

        # ── RIGHT pane ───────────────────────────────────────────────────────
        right = tk.Frame(root_frame, bg=c["bg_primary"], width=200)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        self._section_label(right, "✍️  Підпис")

        sig_row = tk.Frame(right, bg=c["bg_primary"])
        sig_row.pack(fill="x", pady=(4, 0))

        self.sig_label = tk.Label(
            sig_row,
            text="Файл не обрано",
            bg=c["bg_secondary"],
            fg=c["text_tertiary"],
            font=("Segoe UI", 9),
            anchor="w",
            padx=8, pady=6,
            relief="flat",
        )
        self.sig_label.pack(fill="x", pady=(0, 6))

        rounded_button(
            sig_row, "📁  Вибрати PNG",
            self.upload_signature,
            bg=c["bg_tertiary"], fg=c["text_primary"],
            hover_bg=c["border"],
            font=("Segoe UI", 9),
        ).pack(fill="x")

        # Signature section container (to show/hide)
        self.sig_section = sig_row

        self.render_fields()

        tk.Frame(right, bg=c["border"], height=1).pack(fill="x", pady=14)

        # Action buttons

        rounded_button(
            right, "🔒  Генерувати та захистити PDF",
            self.generate_document,
            bg=c["primary"], fg="white",
            hover_bg=c["primary_hover"],
            font=("Segoe UI", 10, "bold"),
            pady=12,
        ).pack(fill="x", pady=(0, 8))

        self.open_btn = rounded_button(
            right, "📄  Відкрити PDF",
            self.open_pdf,
            bg=c["bg_secondary"], fg=c["text_primary"],
            hover_bg=c["bg_tertiary"],
            font=("Segoe UI", 9),
            pady=9,
        )
        self.open_btn.pack(fill="x", pady=(0, 6))
        self.open_btn.config(state="disabled")

        rounded_button(
            right, "📁  Архів файлів",
            self.open_archive,
            bg=c["bg_secondary"], fg=c["text_primary"],
            hover_bg=c["bg_tertiary"],
            font=("Segoe UI", 9),
            pady=9,
        ).pack(fill="x")

    # ─────────────────── field rendering ─────────────────────────────────────

    def on_template_change(self, event=None):
        self.render_fields()

    def render_fields(self):
        for w in self.fields_container.winfo_children():
            w.destroy()
        self.fields = {}

        template = self.template_var.get()

        if template == "Certificate of Achievement":
            self.add_field("Назва курсу",          "combobox", list(self.course_data.keys()))
            self.add_field("Платформа",             "entry",    state="readonly")
            self.add_field("Кількість годин",       "entry",    state="readonly")
            self.add_field("Рівень курсу",          "entry",    state="readonly")
            self.fields["Назва курсу"].bind("<<ComboboxSelected>>", self.update_course_info)
            self.add_field("Прізвище",              "entry")
            self.add_field("Ім'я",                  "entry")
            self.add_field("По батькові",           "entry")
            self.add_field("Номер студентського",   "entry")
            self.add_field("Дата завершення",       "date")

        elif template == "Application Form":
            self.add_field("Прізвище",                         "entry")
            self.add_field("Ім'я",                             "entry")
            self.add_field("По батькові",                      "entry")
            self.add_field("Дата народження",                  "date")
            self.add_field("Контактний телефон",               "entry")
            self.add_field("Електронна пошта",                 "entry")
            self.add_field("Паспорт (серія/номер) або УНЗР",   "entry")
            self.add_field("Освітній рівень",                  "combobox", ["бакалавр", "магістр"])
            specialties = [
                "Інженерія програмного забезпечення",
                "Комп'ютерні науки",
                "Кібербезпека",
                "Інформаційні системи та технології",
                "Телекомунікації та радіотехніка",
            ]
            self.add_field("Спеціальність",                    "combobox", specialties)
            self.add_field("Форма навчання",                   "combobox", ["денна", "заочна", "дистанційна"])

        elif template == "Contract for Education":
            self.add_field("Дата договору",                    "date")
            self.add_field("Прізвище",                         "entry")
            self.add_field("Ім'я",                             "entry")
            self.add_field("По батькові",                      "entry")
            self.add_field("Контактний телефон",               "entry")
            self.add_field("Електронна пошта",                 "entry")
            self.add_field("Паспорт (серія/номер) або УНЗР",   "entry")
            self.add_field("Освітній рівень",                  "combobox", ["бакалавр", "магістр"])
            specialties = [
                "Інженерія програмного забезпечення",
                "Комп'ютерні науки",
                "Кібербезпека",
                "Інформаційні системи та технології",
                "Телекомунікації та радіотехніка",
            ]
            self.add_field("Спеціальність",                    "combobox", specialties)
            self.add_field("Форма навчання",                   "combobox", ["денна", "заочна", "дистанційна"])
            self.add_field("Загальна вартість (грн)",          "entry")
            self.add_field("Варіанти оплати",                  "combobox", ["щомісячно", "півроку"])

        elif template == "Cyberverse Certificate":
            self.add_field("Прізвище",   "entry")
            self.add_field("Ім'я",       "entry")
            self.add_field("По батькові","entry")
            self.add_field("Місце",      "entry")

        elif template == "Cyberverse Participation Certificate":
            self.add_field("Прізвище",   "entry")
            self.add_field("Ім'я",       "entry")
            self.add_field("По батькові","entry")

        self.toggle_signature_section()

    def add_field(self, label, field_type, values=None, state="normal"):
        """Add a label + widget row using grid for uniform alignment."""
        row = len(self.fields)
        c   = self.colors

        # Configure grid weight on container
        self.fields_container.rowconfigure(row, pad=4)

        lbl = tk.Label(
            self.fields_container,
            text=f"{label}:",
            bg=c["bg_primary"],
            fg=c["text_secondary"],
            font=("Segoe UI", 9),
            anchor="w",
            width=self.LABEL_WIDTH,
        )
        lbl.grid(row=row, column=0, sticky="w", pady=4, padx=(0, 10))

        if field_type == "entry":
            widget = ttk.Entry(self.fields_container,
                               font=("Segoe UI", 10),
                               state=state)
        elif field_type == "combobox":
            widget = ttk.Combobox(self.fields_container,
                                  values=values,
                                  state="readonly",
                                  font=("Segoe UI", 10))
        elif field_type == "date":
            widget = DateEntry(
                self.fields_container,
                background=self.colors["primary"],
                foreground="white",
                borderwidth=0,
                font=("Segoe UI", 10),
                date_pattern="dd.mm.yyyy",
            )
        else:
            widget = ttk.Entry(self.fields_container, font=("Segoe UI", 10))

        widget.grid(row=row, column=1, sticky="ew", pady=4)
        self.fields[label] = widget

    def update_course_info(self, event=None):
        course = self.fields["Назва курсу"].get()
        if course in self.course_data:
            info = self.course_data[course]
            for key, val in [
                ("Платформа",       info["platform"]),
                ("Кількість годин", info["hours"]),
                ("Рівень курсу",    info["level"]),
            ]:
                self.fields[key].config(state="normal")
                self.fields[key].delete(0, tk.END)
                self.fields[key].insert(0, val)
                self.fields[key].config(state="readonly")

    def toggle_signature_section(self):
        template = self.template_var.get()
        if template in ("Cyberverse Certificate", "Cyberverse Participation Certificate"):
            self.sig_section.pack_forget()
            self.signature_path = ""
            self.sig_label.config(text="Файл не обрано", fg=self.colors["text_tertiary"])
        else:
            self.sig_section.pack(fill="x", pady=(4, 0))

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — VERIFY
    # ══════════════════════════════════════════════════════════════════════════

    def _build_verify_tab(self):
        c = self.colors
        root_frame = tk.Frame(self.ver_frame, bg=c["bg_primary"])
        root_frame.pack(fill="both", expand=True, padx=28, pady=20)

        self._section_label(root_frame, "🔐  Верифікація документів")
        tk.Frame(root_frame, bg=c["border"], height=1).pack(fill="x", pady=(6, 14))

        # Mode row
        mode_row = tk.Frame(root_frame, bg=c["bg_primary"])
        mode_row.pack(fill="x", pady=(0, 14))

        tk.Label(mode_row, text="Режим:",
                 bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 12))

        self.verification_mode = tk.StringVar(value="single")
        ttk.Radiobutton(mode_row, text="Одинична перевірка",
                        variable=self.verification_mode, value="single").pack(side="left", padx=(0, 20))
        ttk.Radiobutton(mode_row, text="Масова перевірка",
                        variable=self.verification_mode, value="mass").pack(side="left")

        # Buttons row
        btn_row = tk.Frame(root_frame, bg=c["bg_primary"])
        btn_row.pack(fill="x", pady=(0, 16))

        rounded_button(
            btn_row, "🔍  Вибрати для перевірки",
            self.verify_document,
            bg=c["primary"], fg="white",
            hover_bg=c["primary_hover"],
            font=("Segoe UI", 10, "bold"),
            pady=10,
        ).pack(side="left", padx=(0, 10))

        rounded_button(
            btn_row, "📁  Переглянути архів",
            self.open_archive,
            bg=c["bg_secondary"], fg=c["text_primary"],
            hover_bg=c["bg_tertiary"],
            font=("Segoe UI", 9),
            pady=10,
        ).pack(side="left")

        # Progress bar (hidden by default)
        self.verify_progress_var = tk.DoubleVar()
        self.verify_progress = ttk.Progressbar(
            root_frame,
            variable=self.verify_progress_var,
            maximum=100, mode="determinate",
        )
        self.verify_progress.pack(fill="x", pady=(0, 4))
        self.verify_progress.pack_forget()

        self.verify_progress_label = tk.Label(
            root_frame, text="",
            bg=c["bg_primary"], fg=c["text_secondary"],
            font=("Segoe UI", 9), anchor="w",
        )
        self.verify_progress_label.pack(fill="x", pady=(0, 10))

        # Status badge
        status_row = tk.Frame(root_frame, bg=c["bg_primary"])
        status_row.pack(fill="x", pady=(0, 10))

        tk.Label(status_row, text="Статус:",
                 bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 9)).pack(side="left")

        self.status_label = tk.Label(
            status_row,
            text="⏳  Очікування...",
            bg=c["bg_primary"],
            fg=c["text_tertiary"],
            font=("Segoe UI", 12, "bold"),
        )
        self.status_label.pack(side="left", padx=10)

        # Results area
        self._section_label(root_frame, "📋  Результати перевірки")

        text_frame = tk.Frame(root_frame, bg=c["border"], bd=1, relief="solid")
        text_frame.pack(fill="both", expand=True, pady=(6, 0))

        self.result_text = tk.Text(
            text_frame,
            state="disabled",
            bg=c["bg_secondary"],
            fg=c["text_primary"],
            font=("Consolas", 9),
            relief="flat",
            padx=12, pady=12,
            wrap="word",
        )
        vsb = ttk.Scrollbar(text_frame, orient="vertical",
                            command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.result_text.pack(side="left", fill="both", expand=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — MASS GENERATION
    # ══════════════════════════════════════════════════════════════════════════

    def _build_mass_tab(self):
        c = self.colors
        root_frame = tk.Frame(self.mass_frame, bg=c["bg_primary"])
        root_frame.pack(fill="both", expand=True, padx=28, pady=20)

        self._section_label(root_frame, "📦  Масове генерування документів")
        tk.Frame(root_frame, bg=c["border"], height=1).pack(fill="x", pady=(6, 16))

        # ── Template ─────────────────────────────────────────────────────────
        tk.Label(root_frame, text="Шаблон документа:",
                 bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(0, 4))

        self.mass_template_var = tk.StringVar(value="Cyberverse Certificate")
        templates = ["Cyberverse Certificate", "Cyberverse Participation Certificate"]
        styled_combobox(root_frame, templates,
                        textvariable=self.mass_template_var).pack(fill="x", pady=(0, 16))

        # ── CSV file ──────────────────────────────────────────────────────────
        tk.Label(root_frame, text="📄  Вибір CSV файлу:",
                 bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(0, 4))

        self.csv_path_var = tk.StringVar(value="")
        csv_row = tk.Frame(root_frame, bg=c["bg_primary"])
        csv_row.pack(fill="x", pady=(0, 16))

        self.csv_display = tk.Label(
            csv_row,
            textvariable=self.csv_path_var,
            bg=c["bg_secondary"],
            fg=c["text_tertiary"],
            font=("Segoe UI", 9),
            anchor="w",
            padx=8, pady=6,
            relief="flat",
        )
        self.csv_display.pack(side="left", fill="x", expand=True, padx=(0, 8))

        rounded_button(
            csv_row, "📁  Вибрати",
            self.select_csv_file,
            bg=c["bg_tertiary"], fg=c["text_primary"],
            hover_bg=c["border"],
            font=("Segoe UI", 9),
        ).pack(side="right")

        # ── Output folder ─────────────────────────────────────────────────────
        tk.Label(root_frame, text="📁  Папка призначення:",
                 bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(0, 4))

        self.output_folder_var = tk.StringVar(value="generated_archive")
        out_row = tk.Frame(root_frame, bg=c["bg_primary"])
        out_row.pack(fill="x", pady=(0, 16))

        ttk.Entry(out_row,
                  textvariable=self.output_folder_var,
                  font=("Segoe UI", 9),
                  state="readonly").pack(side="left", fill="x", expand=True, padx=(0, 8))

        rounded_button(
            out_row, "📁  Змінити",
            self.select_output_folder,
            bg=c["bg_tertiary"], fg=c["text_primary"],
            hover_bg=c["border"],
            font=("Segoe UI", 9),
        ).pack(side="right")

        # ── Progress ──────────────────────────────────────────────────────────
        self.mass_gen_progress_var = tk.DoubleVar()
        self.mass_gen_progress = ttk.Progressbar(
            root_frame,
            variable=self.mass_gen_progress_var,
            maximum=100, mode="determinate",
        )
        self.mass_gen_progress.pack(fill="x", pady=(0, 4))
        self.mass_gen_progress.pack_forget()

        self.mass_gen_progress_label = tk.Label(
            root_frame, text="",
            bg=c["bg_primary"], fg=c["text_secondary"],
            font=("Segoe UI", 9), anchor="w",
        )
        self.mass_gen_progress_label.pack(fill="x", pady=(0, 10))

        # ── Start button ──────────────────────────────────────────────────────
        self.mass_gen_btn = rounded_button(
            root_frame, "🚀  Почати масове генерування",
            self.start_mass_generation,
            bg=c["primary"], fg="white",
            hover_bg=c["primary_hover"],
            font=("Segoe UI", 10, "bold"),
            pady=11,
        )
        self.mass_gen_btn.pack(fill="x", pady=(0, 16))

        # ── Log ───────────────────────────────────────────────────────────────
        tk.Label(root_frame, text="📋  Лог процесу:",
                 bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(0, 6))

        log_frame = tk.Frame(root_frame, bg=c["border"], bd=1, relief="solid")
        log_frame.pack(fill="both", expand=True)

        self.mass_gen_log = tk.Text(
            log_frame,
            state="disabled",
            bg=c["bg_secondary"],
            fg=c["text_primary"],
            font=("Consolas", 9),
            relief="flat",
            padx=12, pady=12,
        )
        vsb = ttk.Scrollbar(log_frame, orient="vertical",
                            command=self.mass_gen_log.yview)
        self.mass_gen_log.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.mass_gen_log.pack(side="left", fill="both", expand=True)

        rounded_button(
            root_frame, "📁  Відкрити папку з файлами",
            self.open_archive,
            bg=c["bg_secondary"], fg=c["text_primary"],
            hover_bg=c["bg_tertiary"],
            font=("Segoe UI", 9),
            pady=8,
        ).pack(fill="x", pady=(10, 0))

    # ══════════════════════════════════════════════════════════════════════════
    # SHARED HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _section_label(self, parent, text):
        tk.Label(
            parent, text=text,
            bg=self.colors["bg_primary"],
            fg=self.colors["text_primary"],
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 2))

    # ── signature ─────────────────────────────────────────────────────────────

    def upload_signature(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png")])
        if file_path:
            self.signature_path = file_path
            self.sig_label.config(
                text=os.path.basename(file_path),
                fg=self.colors["success"],
            )

    # ── generate ─────────────────────────────────────────────────────────────

    def generate_document(self):
        personal_data = {label: entry.get().strip()
                         for label, entry in self.fields.items()}

        missing_fields = [label for label, value in personal_data.items() if not value]

        template = self.template_var.get()
        if template not in ("Cyberverse Certificate",
                             "Cyberverse Participation Certificate"):
            if not self.signature_path:
                missing_fields.append("Підпис (картинка)")

        if missing_fields:
            messagebox.showwarning(
                "Заповніть всі дані",
                "Будь ласка, заповніть всі поля:\n\n" +
                "\n".join(f"• {f}" for f in missing_fields),
            )
            return

        personal_data = {k: v for k, v in personal_data.items() if v}

        # Normalize apostrophe in name
        for key in ("Ім'я", "Ім'я"):
            if key in personal_data:
                personal_data[key] = personal_data[key].replace("'", "\u2019")

        # Auto contract number
        if template == "Contract for Education":
            import datetime
            now = datetime.datetime.now()
            personal_data["Номер договору"] = f"КНУ-{now.year}-{now.strftime('%f')[:4]}"

        # Passport validation
        passport_key = next(
            (k for k in ("Паспорт (серія/номер) або УНЗР", "Номер ID")
             if k in personal_data), None)
        if passport_key:
            try:
                from validators import validate_passport_ua
                personal_data[passport_key] = validate_passport_ua(
                    personal_data[passport_key])
            except ValueError as ve:
                messagebox.showerror("Помилка валідації документа", str(ve))
                return

        # Phone validation
        if "Контактний телефон" in personal_data:
            try:
                from crypto_utils import CryptoManager
                personal_data["Контактний телефон"] = CryptoManager.validate_phone_ua(
                    personal_data["Контактний телефон"])
            except ValueError as ve:
                messagebox.showerror("Помилка валідації телефону", str(ve))
                return

        # Amount validation
        if template == "Contract for Education":
            try:
                from crypto_utils import CryptoManager
                personal_data["Загальна вартість (грн)"] = CryptoManager.validate_amount_ua(
                    personal_data.get("Загальна вартість (грн)", ""))
            except ValueError as ve:
                messagebox.showerror("Помилка валідації суми", str(ve))
                return

        personal_data = {k: v for k, v in personal_data.items() if v}

        try:
            output_pdf = self.system.user_workflow(
                template, personal_data, self.signature_path)
            self.last_generated_pdf = output_pdf
            self.open_btn.config(state="normal")
            messagebox.showinfo(
                "Успіх",
                f"Захищений документ успішно створено:\n{output_pdf}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при генерації:\n{e}")

    def open_pdf(self):
        if self.last_generated_pdf and os.path.exists(self.last_generated_pdf):
            os.startfile(self.last_generated_pdf)

    def open_archive(self):
        archive_dir = "generated_archive"
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        os.startfile(os.path.abspath(archive_dir))

    # ── verify ────────────────────────────────────────────────────────────────

    def verify_document(self):
        mode = self.verification_mode.get()

        if mode == "single":
            file_path = filedialog.askopenfilename(
                filetypes=[("PDF files", "*.pdf")])
            if not file_path:
                return

            self.status_label.config(
                text="⏳  ПЕРЕВІРКА...",
                fg=self.colors["primary"])
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "Запуск процесу верифікації...\n")
            self.result_text.config(state="disabled")
            self.root.update_idletasks()

            def run_single():
                import sys, io
                old = sys.stdout
                sys.stdout = buf = io.StringIO()
                try:
                    self.system.admin_workflow(file_path)
                    output = buf.getvalue()
                    self.root.after(
                        0, lambda: self.update_verification_results(output))
                except Exception as e:
                    self.root.after(
                        0, lambda: messagebox.showerror(
                            "Помилка", f"Помилка при верифікації:\n{e}"))
                    self.root.after(
                        0, lambda: self.status_label.config(
                            text="❌  ПОМИЛКА",
                            fg=self.colors["danger"]))
                finally:
                    sys.stdout = old

            import threading
            threading.Thread(target=run_single, daemon=True).start()
            return

        # Mass verification
        folder_path = filedialog.askdirectory(
            title="Виберіть папку з PDF файлами")
        if not folder_path:
            return

        pdf_count = len([f for f in os.listdir(folder_path)
                         if f.lower().endswith(".pdf")])
        if pdf_count == 0:
            messagebox.showwarning(
                "Увага",
                f"У вибраній папці не знайдено PDF-файлів.\nШлях: {folder_path}")
            return

        self.run_mass_verification(folder_path)

    def update_verification_results(self, output):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, output)
        self.result_text.config(state="disabled")
        self.result_text.see(tk.END)

        c = self.colors
        if "STATUS: VALID" in output:
            self.status_label.config(text="✅  ВАЛІДНИЙ",   fg=c["success"])
        elif "STATUS: TAMPERED" in output:
            self.status_label.config(text="⚠️  ПОШКОДЖЕНИЙ", fg=c["danger"])
        else:
            self.status_label.config(text="❌  ПОМИЛКА",    fg=c["warning"])

    def run_mass_verification(self, folder_path):
        import threading, sys
        from io import StringIO

        pdf_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(".pdf")
        ]
        if not pdf_files:
            messagebox.showwarning(
                "Увага",
                f"У папці {folder_path} не знайдено PDF файлів.")
            return

        self.verify_progress.pack(fill="x", pady=(0, 4))
        self.verify_progress_var.set(0)
        self.status_label.config(
            text="⏳  МАСОВА ПЕРЕВІРКА...",
            fg=self.colors["primary"])
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(
            tk.END,
            f"Знайдено {len(pdf_files)} файлів для перевірки.\n\n")
        self.result_text.config(state="disabled")

        def run_batch():
            valid = tampered = errors = 0
            old_diag = self.system.diagnostic_mode
            self.system.diagnostic_mode = False

            for i, pdf_path in enumerate(pdf_files):
                filename = os.path.basename(pdf_path)
                progress = (i + 1) / len(pdf_files) * 100
                self.root.after(
                    0,
                    lambda p=progress, f=filename, idx=i+1:
                        self._update_mass_verify_progress(p, f, idx, len(pdf_files)))

                old_out = sys.stdout
                sys.stdout = buf = StringIO()
                try:
                    self.system.admin_workflow(pdf_path)
                    sys.stdout = old_out
                    res = buf.getvalue()
                    if "[RESULT] STATUS: VALID" in res:
                        status = "✅ VALID"; valid += 1
                    elif "TAMPERED" in res:
                        status = "❌ TAMPERED"; tampered += 1
                    elif "UNSIGNED" in res:
                        status = "⚠️ UNSIGNED"; errors += 1
                    else:
                        status = "❓ UNKNOWN"; errors += 1
                    self.root.after(
                        0, lambda fn=filename, st=status:
                            self._append_verify_result(fn, st))
                except Exception as e:
                    sys.stdout = old_out
                    errors += 1
                    self.root.after(
                        0, lambda fn=filename, err=str(e):
                            self._append_verify_result(fn, f"💥 ERROR: {err}"))

            self.system.diagnostic_mode = old_diag
            total = len(pdf_files)
            summary = (
                f"\n{'='*50}\n--- Підсумок перевірки ---\n"
                f"Всього файлів: {total}\n"
                f"Валідних:      {valid}\n"
                f"Пошкоджених:   {tampered}\n"
                f"Інші (помилки): {errors}\n"
            )
            self.root.after(
                0, lambda s=summary:
                    self._finish_mass_verification(s, valid, tampered, errors, total))

        threading.Thread(target=run_batch, daemon=True).start()

    def _update_mass_verify_progress(self, progress, filename, idx, total):
        self.verify_progress_var.set(progress)
        self.verify_progress_label.config(
            text=f"[{idx}/{total}] Перевірка: {filename}...")

    def _append_verify_result(self, filename, status):
        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, f"{filename}: {status}\n")
        self.result_text.config(state="disabled")
        self.result_text.see(tk.END)

    def _finish_mass_verification(self, summary, valid, tampered, error, total):
        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, summary)
        self.result_text.config(state="disabled")
        self.result_text.see(tk.END)
        self.verify_progress.pack_forget()
        self.verify_progress_label.config(text="")
        c = self.colors
        if error == 0 and tampered == 0 and valid == total:
            self.status_label.config(text="✅  ВСІ ВАЛІДНІ", fg=c["success"])
        elif tampered > 0:
            self.status_label.config(
                text=f"⚠️  ЗНАЙДЕНО ПОШКОДЖЕНІ ({tampered})", fg=c["danger"])
        else:
            self.status_label.config(
                text=f"✅  ПЕРЕВІРЕНО ({valid}/{total})", fg=c["warning"])

    # ── mass generation ───────────────────────────────────────────────────────

    def select_csv_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            self.csv_path_var.set(file_path)
            self.csv_display.config(fg=self.colors["success"])

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(
            title="Виберіть папку призначення")
        if folder_path:
            self.output_folder_var.set(folder_path)

    def start_mass_generation(self):
        csv_path      = self.csv_path_var.get()
        template_type = self.mass_template_var.get()
        output_folder = self.output_folder_var.get()

        if not csv_path:
            messagebox.showwarning("Увага",
                                   "Будь ласка, виберіть CSV файл з даними.")
            return
        if not os.path.exists(csv_path):
            messagebox.showerror("Помилка", f"Файл {csv_path} не знайдено.")
            return

        self.mass_gen_btn.config(state="disabled")
        self.mass_gen_log.config(state="normal")
        self.mass_gen_log.delete("1.0", tk.END)
        self.mass_gen_log.insert(
            tk.END,
            f"Початок масового генерування...\nШаблон: {template_type}\n\n")
        self.mass_gen_log.config(state="disabled")
        self.mass_gen_progress_var.set(0)

        import threading
        threading.Thread(
            target=self.run_mass_generation,
            args=(csv_path, template_type, output_folder),
            daemon=True,
        ).start()

    def run_mass_generation(self, csv_path, template_type, output_folder):
        import csv

        try:
            with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                sample = f.read(1024)
                f.seek(0)
                try:
                    detected_delimiter = csv.Sniffer().sniff(
                        sample, delimiters=",;").delimiter
                except csv.Error:
                    detected_delimiter = ";"

                reader    = csv.reader(f, delimiter=detected_delimiter)
                all_lines = list(reader)

                if not all_lines:
                    self.root.after(
                        0, lambda: messagebox.showerror(
                            "Помилка", f"Файл {csv_path} порожній."))
                    self.root.after(
                        0, lambda: self.mass_gen_btn.config(state="normal"))
                    return

                fieldnames = [n.strip() for n in all_lines[0]]
                rows = []
                for line in all_lines[1:]:
                    if not line or not any(line):
                        continue
                    row = {}
                    for i, val in enumerate(line):
                        if i < len(fieldnames):
                            row[fieldnames[i]] = val.strip()
                    rows.append(row)

                self.root.after(
                    0, lambda fn=", ".join(fieldnames), d=detected_delimiter:
                        self._log_mass_gen(
                            f"Знайдено полів: {fn} (Роздільник: '{d}')\n"))

                def find_val(row_dict, aliases):
                    norm = [a.lower().strip().replace("'", "\u2019")
                            for a in aliases]
                    for k, v in row_dict.items():
                        if k.lower().strip().replace("'", "\u2019") in norm:
                            return str(v).strip()
                    return ""

                count = 0
                total = len(rows)
                for idx, row in enumerate(rows):
                    if "Cyberverse" in template_type:
                        prizv = find_val(row, ["Прізвище", "Surname", "Last Name"])
                        imya  = find_val(row, ["Ім'я", "Ім\u2019я", "Name", "First Name"])
                        pobat = find_val(row, ["По батькові", "Middle Name", "Patronymic"])
                        place = ("" if template_type == "Cyberverse Participation Certificate"
                                 else find_val(row, ["Місце", "Зайняте місце", "Place", "Rank"]))
                        name  = f"{prizv} {imya} {pobat}".strip() or find_val(
                            row, ["ПІБ", "Full Name", "Name"])
                        row["Прізвище"]   = prizv
                        row["Ім'я"]       = imya
                        row["По батькові"] = pobat
                        row["Місце"]      = place
                    else:
                        imya_other = row.get("Ім'я") or row.get("Ім\u2019я") or ""
                        row["Ім'я"] = imya_other
                        name = f"{row.get('Прізвище', '')} {imya_other}".strip()

                    progress = (idx + 1) / total * 100
                    self.root.after(
                        0, lambda p=progress, n=name, i=idx+1, t=total:
                            self._update_mass_gen_progress(p, n, i, t))

                    try:
                        output_file = self.system.user_workflow(
                            template_type, row)
                        count += 1
                        self.root.after(
                            0, lambda n=name, fn=os.path.basename(output_file):
                                self._log_mass_gen(
                                    f"✅ [{count}] {n} → {fn}\n"))
                    except Exception as e:
                        self.root.after(
                            0, lambda n=name, err=str(e):
                                self._log_mass_gen(
                                    f"❌ Помилка для {n}: {err}\n"))

                summary = (
                    f"\n{'='*50}\n"
                    f"✅ Успішно згенеровано {count} документів.\n"
                    f"📁 Файли збережено в папці: {output_folder}\n"
                )
                self.root.after(
                    0, lambda s=summary: self._finish_mass_generation(s))

        except Exception as e:
            self.root.after(
                0, lambda err=str(e):
                    messagebox.showerror(
                        "Помилка", f"Помилка при читанні CSV:\n{err}"))
            self.root.after(
                0, lambda: self.mass_gen_btn.config(state="normal"))

    def _update_mass_gen_progress(self, progress, name, idx, total):
        self.mass_gen_progress_var.set(progress)
        self.mass_gen_progress_label.config(
            text=f"[{idx}/{total}] Обробка: {name}...")

    def _log_mass_gen(self, message):
        self.mass_gen_log.config(state="normal")
        self.mass_gen_log.insert(tk.END, message)
        self.mass_gen_log.config(state="disabled")
        self.mass_gen_log.see(tk.END)

    def _finish_mass_generation(self, summary):
        self._log_mass_gen(summary)
        self.mass_gen_btn.config(state="normal")
        self.mass_gen_progress_label.config(text="✅ Завершено!")
        messagebox.showinfo("Успіх",
                            "Масове генерування завершено успішно!")


# ─────────────────────────── Entry point ─────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = ProtectionApp(root)
    root.mainloop()