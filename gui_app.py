import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime
import threading
from tkcalendar import DateEntry
from main import DocumentProtectionSystem


# ─────────────────────────── Rounded Helpers & Custom Widgets ───────────────────────────────

def create_rounded_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Малює справжній заокруглений прямокутник на Canvas."""
    points = [x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
              x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, x2, y2 - radius,
              x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius, y2, x1 + radius, y2,
              x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)


class RoundedButton(tk.Canvas):
    """Кастомна заокруглена кнопка."""

    def __init__(self, parent, text, command, bg, fg, hover_bg, radius=10, width=200, height=42,
                 font=("Segoe UI", 10, "bold"), **kwargs):
        parent_bg = kwargs.pop("parent_bg", "#FFFFFF")
        super().__init__(parent, width=width, height=height, bg=parent_bg, highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg
        self.hover_bg = hover_bg
        self.fg_color = fg
        self.radius = radius
        self.is_disabled = False

        self.rect_id = create_rounded_rect(self, 2, 2, width - 2, height - 2, radius=self.radius, fill=self.bg_color,
                                           outline="")
        self.text_id = self.create_text(width / 2, height / 2, text=text, fill=self.fg_color, font=font,
                                        justify="center")

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.config(cursor="hand2")

    def on_enter(self, event):
        if not self.is_disabled:
            self.itemconfig(self.rect_id, fill=self.hover_bg)

    def on_leave(self, event):
        if not self.is_disabled:
            self.itemconfig(self.rect_id, fill=self.bg_color)

    def on_click(self, event):
        if not self.is_disabled:
            self.move(self.text_id, 0, 1)
            self.move(self.rect_id, 0, 1)

    def on_release(self, event):
        if not self.is_disabled:
            self.move(self.text_id, 0, -1)
            self.move(self.rect_id, 0, -1)
            if self.command:
                self.after(50, self.command)

    def config_state(self, state):
        self.is_disabled = (state == "disabled")
        if self.is_disabled:
            self.itemconfig(self.rect_id, fill="#D1D5DB")
            self.itemconfig(self.text_id, fill="#9CA3AF")
            self.config(cursor="arrow")
        else:
            self.itemconfig(self.rect_id, fill=self.bg_color)
            self.itemconfig(self.text_id, fill=self.fg_color)
            self.config(cursor="hand2")


class RoundedEntry(tk.Frame):
    """Кастомне заокруглене поле вводу."""

    def __init__(self, parent, width=35, font=("Segoe UI", 10), parent_bg="#FFFFFF", state="normal", **kwargs):
        super().__init__(parent, bg=parent_bg)
        self.canvas = tk.Canvas(self, width=width * 8, height=36, bg=parent_bg, highlightthickness=0)
        self.canvas.pack(fill="x", expand=True)

        # Визначаємо початковий колір
        bg_col = "#E5E7EB" if state in ["readonly", "disabled"] else "#F9FAFB"
        self.rect_id = create_rounded_rect(self.canvas, 2, 2, width * 8 - 2, 34, radius=10, fill=bg_col,
                                           outline="#E5E7EB")

        # Додано readonlybackground="#E5E7EB" для вирішення проблеми чорного фону
        self.entry = tk.Entry(
            self.canvas, bd=0, bg=bg_col, highlightthickness=0, font=font,
            fg="#111827", disabledbackground="#E5E7EB", readonlybackground="#E5E7EB"
        )
        self.entry.config(state=state)
        self.canvas.create_window(10, 18, window=self.entry, anchor="w", width=width * 8 - 20)

    def get(self):
        return self.entry.get()

    def insert(self, index, string):
        was_readonly = self.entry.cget("state") == "readonly"
        if was_readonly: self.entry.config(state="normal")
        self.entry.insert(index, string)
        if was_readonly: self.entry.config(state="readonly")

    def delete(self, first, last=None):
        was_readonly = self.entry.cget("state") == "readonly"
        if was_readonly: self.entry.config(state="normal")
        self.entry.delete(first, last)
        if was_readonly: self.entry.config(state="readonly")

    def config(self, **kwargs):
        if "state" in kwargs:
            bg_col = "#E5E7EB" if kwargs["state"] in ["readonly", "disabled"] else "#F9FAFB"
            self.canvas.itemconfig(self.rect_id, fill=bg_col)
            self.entry.config(bg=bg_col)
        self.entry.config(**kwargs)

# ─────────────────────────── Animated Notebook ───────────────────────────────

class AnimatedNotebook(tk.Frame):
    ANIM_STEPS = 8
    ANIM_DELAY = 15

    def __init__(self, parent, colors, **kwargs):
        super().__init__(parent, bg=colors["bg_primary"], **kwargs)
        self.colors = colors
        self._tabs = []
        self._current = 0
        self._anim_id = None

        self._bar = tk.Frame(self, bg=colors["bg_primary"])
        self._bar.pack(side="top", fill="x", pady=(10, 0), padx=20)
        self._accent = tk.Frame(self, bg=colors["border"], height=1)
        self._accent.pack(side="top", fill="x", padx=20)

        self._content = tk.Frame(self, bg=colors["bg_primary"])
        self._content.pack(side="top", fill="both", expand=True)

    def add(self, frame, text: str):
        idx = len(self._tabs)
        self._tabs.append((text, frame))
        btn = tk.Button(
            self._bar, text=text, bd=0, relief="flat", cursor="hand2", font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg_primary"], fg=self.colors["text_secondary"], activebackground=self.colors["bg_primary"],
            activeforeground=self.colors["primary"], padx=20, pady=8, command=lambda i=idx: self._select(i)
        )
        btn.pack(side="left", padx=5)
        frame.place(in_=self._content, x=0, y=0, relwidth=1, relheight=1)
        frame.lower()
        if idx == 0: self._show_tab(0, animate=False)

    def _select(self, idx: int):
        if idx == self._current: return
        if self._anim_id: self.after_cancel(self._anim_id)
        self._show_tab(idx)

    def _show_tab(self, idx: int, animate: bool = True):
        self._current = idx
        _, frame = self._tabs[idx]
        frame.lift()
        self._update_tab_bar()

    def _update_tab_bar(self):
        for i, btn in enumerate(self._bar.winfo_children()):
            if isinstance(btn, tk.Button):
                if i == self._current:
                    btn.config(fg=self.colors["primary"], font=("Segoe UI", 11, "bold"))
                else:
                    btn.config(fg=self.colors["text_secondary"], font=("Segoe UI", 11))


# ─────────────────────────── Main Application ────────────────────────────────

class ProtectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система захисту PDF документів")
        self.root.geometry("1080x760")
        self.root.minsize(980, 720)
        self.root.resizable(True, True)  # Дозволено повноекранний режим

        self.colors = {
            "bg_primary": "#FFFFFF",
            "bg_secondary": "#F9FAFB",
            "bg_tertiary": "#F3F4F6",
            "primary": "#2563EB",
            "primary_hover": "#1D4ED8",
            "success": "#10B981",
            "danger": "#EF4444",
            "text_primary": "#111827",  # Контрастний чорний-сірий
            "text_secondary": "#4B5563",
            "text_tertiary": "#9CA3AF",
            "border": "#E5E7EB",
        }

        self.system = DocumentProtectionSystem()
        self.system.create_dummy_assets()
        self.bg_template_path = os.path.join("png", "background_template.png")

        self._configure_styles()
        self.root.configure(bg=self.colors["bg_primary"])

        self.notebook = AnimatedNotebook(self.root, self.colors)
        self.notebook.pack(fill="both", expand=True)

        self.gen_frame = tk.Frame(self.notebook, bg=self.colors["bg_primary"])
        self.ver_frame = tk.Frame(self.notebook, bg=self.colors["bg_primary"])
        self.mass_frame = tk.Frame(self.notebook, bg=self.colors["bg_primary"])

        self.notebook.add(self.gen_frame, text="  📝 ОДИНОЧНЕ ГЕНЕРУВАННЯ  ")
        self.notebook.add(self.mass_frame, text="  📦 МАСОВЕ ГЕНЕРУВАННЯ  ")
        self.notebook.add(self.ver_frame, text="  🔍 ПЕРЕВІРКА  ")

        self.course_data = {
            "Introduction to Cybersecurity": {"platform": "Cisco", "hours": "15", "level": "Beginner"},
            "Cybersecurity Essentials": {"platform": "Cisco", "hours": "30", "level": "Intermediate"},
            "Network Security": {"platform": "Cisco", "hours": "40", "level": "Advanced"},
            "Ethical Hacking (Cisco NetAcad)": {"platform": "Cisco", "hours": "70", "level": "Advanced"},
            "Google Cybersecurity Professional Certificate": {"platform": "Coursera", "hours": "180",
                                                              "level": "Professional"},
            "IBM Cybersecurity Analyst": {"platform": "Coursera", "hours": "120", "level": "Intermediate"},
            "Cybersecurity Specialization (Maryland)": {"platform": "Coursera", "hours": "90", "level": "Advanced"},
            "Applied Cryptography": {"platform": "Coursera", "hours": "45", "level": "Advanced"},
        }

        self._build_generate_tab()
        self._build_mass_tab()
        self._build_verify_tab()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#F9FAFB", background="#FFFFFF", bordercolor="#E5E7EB", padding=5,
                        font=("Segoe UI", 10))
        style.configure("TProgressbar", thickness=10, background=self.colors["primary"],
                        troughcolor=self.colors["bg_tertiary"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — GENERATE
    # ══════════════════════════════════════════════════════════════════════════
    def _build_generate_tab(self):
        c = self.colors
        container = tk.Frame(self.gen_frame, bg=c["bg_primary"], padx=30, pady=20)
        container.pack(fill="both", expand=True)

        top_row = tk.Frame(container, bg=c["bg_primary"])
        top_row.pack(fill="x", pady=(0, 15))

        tk.Label(top_row, text="Тип документа:", bg=c["bg_primary"], fg=c["text_primary"],
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        self.template_var = tk.StringVar(value="Cyberverse Certificate")
        templates = ["Cyberverse Certificate", "Cyberverse Participation Certificate", "Certificate of Achievement",
                     "Application Form", "Contract for Education"]
        self.template_cb = ttk.Combobox(top_row, values=templates, textvariable=self.template_var, state="readonly",
                                        width=40, font=("Segoe UI", 10))
        self.template_cb.pack(side="left")
        self.template_cb.bind("<<ComboboxSelected>>", self.on_template_change)

        main_content = tk.Frame(container, bg=c["bg_primary"])
        main_content.pack(fill="both", expand=True)

        left_col = tk.Frame(main_content, bg=c["bg_primary"])
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(left_col, text="Персональні дані:", bg=c["bg_primary"], fg=c["primary"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        # Grid Container for 2 Columns
        self.fields_container = tk.Frame(left_col, bg=c["bg_primary"])
        self.fields_container.pack(fill="both", expand=True)

        right_col = tk.Frame(main_content, bg=c["bg_secondary"], padx=20, pady=20, bd=1, relief="solid")
        right_col.config(highlightbackground=c["border"], highlightthickness=1)
        right_col.pack(side="right", fill="y", ipadx=10)

        # Signature Section
        self.sig_section = tk.Frame(right_col, bg=c["bg_secondary"])
        self.sig_section.pack(fill="x", pady=(0, 20))
        tk.Label(self.sig_section, text="Електронний підпис (Опціонально)", bg=c["bg_secondary"], fg=c["text_primary"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.sig_label = tk.Label(self.sig_section, text="Файл не обрано", bg=c["bg_secondary"], fg=c["text_tertiary"],
                                  font=("Segoe UI", 9))
        self.sig_label.pack(anchor="w", pady=5)
        self.btn_select_sig = RoundedButton(self.sig_section, text="Обрати PNG", command=self.upload_signature,
                                            bg=c["bg_tertiary"], fg=c["text_primary"], hover_bg=c["border"], width=180,
                                            height=36, parent_bg=c["bg_secondary"])
        self.btn_select_sig.pack(anchor="w")
        self.signature_path = ""
        self.last_generated_pdf = ""

        # Status & Generate
        self.gen_btn = RoundedButton(right_col, text="🔒 Генерувати та захистити", command=self.generate_document,
                                     bg=c["primary"], fg="#FFFFFF", hover_bg=c["primary_hover"], width=220, height=45,
                                     parent_bg=c["bg_secondary"])
        self.gen_btn.pack(pady=(20, 10))

        self.open_btn = RoundedButton(right_col, text="📄 Відкрити PDF", command=self.open_pdf, bg=c["success"],
                                      fg="#FFFFFF", hover_bg="#059669", width=220, height=38,
                                      parent_bg=c["bg_secondary"])
        self.open_btn.pack(pady=5)
        self.open_btn.config_state("disabled")

        self.archive_btn = RoundedButton(right_col, text="📁 Архів файлів", command=self.open_archive,
                                         bg=c["bg_tertiary"], fg=c["text_primary"], hover_bg=c["border"], width=220,
                                         height=38, parent_bg=c["bg_secondary"])
        self.archive_btn.pack(pady=5)

        self.render_fields()

    def on_template_change(self, event=None):
        self.render_fields()
        self.toggle_signature_section()

    def render_fields(self):
        for w in self.fields_container.winfo_children(): w.destroy()
        self.fields = {}
        template = self.template_var.get()

        if template == "Certificate of Achievement":
            self.add_field("Назва курсу", "combobox", list(self.course_data.keys()))
            self.add_field("Платформа", "entry", state="readonly")
            self.add_field("Кількість годин", "entry", state="readonly")
            self.add_field("Рівень курсу", "entry", state="readonly")
            self.fields["Назва курсу"].bind("<<ComboboxSelected>>", self.update_course_info)
            self.add_field("Прізвище", "entry")
            self.add_field("Ім'я", "entry")
            self.add_field("По батькові", "entry")
            self.add_field("Номер студентського", "entry")
            self.add_field("Дата завершення", "date")
        elif template == "Application Form":
            self.add_field("Прізвище", "entry")
            self.add_field("Ім'я", "entry")
            self.add_field("По батькові", "entry")
            self.add_field("Дата народження", "date")
            self.add_field("Контактний телефон", "entry")
            self.add_field("Електронна пошта", "entry")
            self.add_field("Паспорт (серія/номер) або УНЗР", "entry")
            self.add_field("Освітній рівень", "combobox", ["бакалавр", "магістр"])
            self.add_field("Спеціальність", "combobox",
                           ["Інженерія програмного забезпечення", "Комп'ютерні науки", "Кібербезпека",
                            "Інформаційні системи та технології"])
            self.add_field("Форма навчання", "combobox", ["денна", "заочна", "дистанційна"])
        elif template == "Contract for Education":
            self.add_field("Дата договору", "date")
            self.add_field("Прізвище", "entry")
            self.add_field("Ім'я", "entry")
            self.add_field("По батькові", "entry")
            self.add_field("Контактний телефон", "entry")
            self.add_field("Електронна пошта", "entry")
            self.add_field("Паспорт (серія/номер) або УНЗР", "entry")
            self.add_field("Освітній рівень", "combobox", ["бакалавр", "магістр"])
            self.add_field("Спеціальність", "combobox",
                           ["Інженерія програмного забезпечення", "Комп'ютерні науки", "Кібербезпека"])
            self.add_field("Форма навчання", "combobox", ["денна", "заочна", "дистанційна"])
            self.add_field("Загальна вартість (грн)", "entry")
            self.add_field("Варіанти оплати", "combobox", ["щомісячно", "півроку"])
        elif template == "Cyberverse Certificate":
            self.add_field("Прізвище", "entry")
            self.add_field("Ім'я", "entry")
            self.add_field("По батькові", "entry")
            self.add_field("Місце", "entry")
        elif template == "Cyberverse Participation Certificate":
            self.add_field("Прізвище", "entry")
            self.add_field("Ім'я", "entry")
            self.add_field("По батькові", "entry")

        self.toggle_signature_section()

    def add_field(self, label, field_type, values=None, state="normal"):
        c = self.colors
        col_pair = (len(self.fields) % 2) * 2
        row = len(self.fields) // 2

        frame = tk.Frame(self.fields_container, bg=c["bg_primary"])
        frame.grid(row=row, column=col_pair, sticky="w", padx=(0, 30), pady=6)

        tk.Label(frame, text=label + ":", bg=c["bg_primary"], fg=c["text_secondary"], font=("Segoe UI", 9)).pack(
            anchor="w")

        if field_type == "entry":
            widget = RoundedEntry(frame, width=32, parent_bg=c["bg_primary"], state=state)
        elif field_type == "combobox":
            widget = ttk.Combobox(frame, values=values, state="readonly" if state == "normal" else "disabled",
                                  font=("Segoe UI", 10), width=30)
        elif field_type == "date":
            widget = DateEntry(frame, width=29, background=c["primary"], foreground="white", borderwidth=0,
                               font=("Segoe UI", 10), date_pattern="dd.mm.yyyy")

        widget.pack(fill="x", pady=2)
        self.fields[label] = widget

    def update_course_info(self, event=None):
        course = self.fields["Назва курсу"].get()
        if course in self.course_data:
            info = self.course_data[course]
            for key, val in [("Платформа", info["platform"]), ("Кількість годин", info["hours"]),
                             ("Рівень курсу", info["level"])]:
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

    def upload_signature(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if path:
            self.signature_path = path
            self.sig_label.config(text=os.path.basename(path), fg=self.colors["success"])

    def generate_document(self):
        personal_data = {label: entry.get().strip() if not isinstance(entry, DateEntry) else entry.get() for
                         label, entry in self.fields.items()}
        missing_fields = [label for label, value in personal_data.items() if not value]

        template = self.template_var.get()
        if template not in ("Cyberverse Certificate", "Cyberverse Participation Certificate"):
            if not self.signature_path: missing_fields.append("Підпис (картинка)")

        if missing_fields:
            messagebox.showwarning("Заповніть всі дані",
                                   "Будь ласка, заповніть всі поля:\n\n" + "\n".join(f"• {f}" for f in missing_fields))
            return

        for key in ("Ім'я", "Ім'я"):
            if key in personal_data: personal_data[key] = personal_data[key].replace("'", "\u2019")

        if template == "Contract for Education":
            now = datetime.datetime.now()
            personal_data["Номер договору"] = f"КНУ-{now.year}-{now.strftime('%f')[:4]}"

        # Валідації
        passport_key = next((k for k in ("Паспорт (серія/номер) або УНЗР", "Номер ID") if k in personal_data), None)
        if passport_key:
            try:
                from validators import validate_passport_ua
                personal_data[passport_key] = validate_passport_ua(personal_data[passport_key])
            except ValueError as ve:
                return messagebox.showerror("Помилка валідації документа", str(ve))

        if "Контактний телефон" in personal_data:
            try:
                from crypto_utils import CryptoManager
                personal_data["Контактний телефон"] = CryptoManager.validate_phone_ua(
                    personal_data["Контактний телефон"])
            except ValueError as ve:
                return messagebox.showerror("Помилка валідації телефону", str(ve))

        if template == "Contract for Education":
            try:
                from crypto_utils import CryptoManager
                personal_data["Загальна вартість (грн)"] = CryptoManager.validate_amount_ua(
                    personal_data.get("Загальна вартість (грн)", ""))
            except ValueError as ve:
                return messagebox.showerror("Помилка валідації суми", str(ve))

        try:
            self.gen_btn.config_state("disabled")
            # ВИКЛИК ОРИГІНАЛЬНОЇ ФУНКЦІЇ З MAIN.PY
            output_pdf = self.system.user_workflow(template, personal_data,
                                                   self.signature_path if self.signature_path else None)

            self.last_generated_pdf = output_pdf
            self.open_btn.config_state("normal")
            messagebox.showinfo("Успіх", f"Захищений документ успішно створено:\n{output_pdf}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при генерації:\n{e}")
        finally:
            self.gen_btn.config_state("normal")

    def open_pdf(self):
        if self.last_generated_pdf and os.path.exists(self.last_generated_pdf):
            os.startfile(self.last_generated_pdf)

    def open_archive(self):
        folder = "generated_archive"
        if not os.path.exists(folder): os.makedirs(folder)
        os.startfile(os.path.abspath(folder))

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — MASS GENERATION (Перероблено на Grid без скролу)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_mass_tab(self):
        c = self.colors
        wrapper = tk.Frame(self.mass_frame, bg=c["bg_primary"], padx=30, pady=20)
        wrapper.pack(fill="both", expand=True)

        tk.Label(wrapper, text="📦 Масове генерування документів", font=("Segoe UI", 16, "bold"), bg=c["bg_primary"],
                 fg=c["text_primary"]).pack(anchor="w", pady=(0, 15))

        cols_frame = tk.Frame(wrapper, bg=c["bg_primary"])
        cols_frame.pack(fill="both", expand=True)

        left_col = tk.Frame(cols_frame, bg=c["bg_primary"])
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(left_col, text="1. Шаблон документа:", bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.mass_template_var = tk.StringVar(value="Cyberverse Certificate")
        mass_cb = ttk.Combobox(left_col, values=["Cyberverse Certificate", "Cyberverse Participation Certificate",
                                                 "Certificate of Achievement", "Application Form"],
                               textvariable=self.mass_template_var, state="readonly", font=("Segoe UI", 10))
        mass_cb.pack(fill="x", pady=(0, 15))

        tk.Label(left_col, text="2. CSV файл з даними:", bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        csv_row = tk.Frame(left_col, bg=c["bg_primary"])
        csv_row.pack(fill="x", pady=(0, 15))
        self.csv_path_var = tk.StringVar(value="Не вибрано")
        tk.Label(csv_row, textvariable=self.csv_path_var, bg=c["bg_secondary"], fg=c["text_primary"], width=30,
                 anchor="w", padx=10, pady=8).pack(side="left", expand=True, fill="x")
        RoundedButton(csv_row, text="Огляд", command=self.select_csv_file, bg=c["bg_tertiary"], fg=c["text_primary"],
                      hover_bg=c["border"], width=100, height=36, parent_bg=c["bg_primary"]).pack(side="right",
                                                                                                  padx=(10, 0))

        tk.Label(left_col, text="3. Папка збереження:", bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        out_row = tk.Frame(left_col, bg=c["bg_primary"])
        out_row.pack(fill="x", pady=(0, 25))
        self.output_folder_var = tk.StringVar(value="generated_archive")
        tk.Label(out_row, textvariable=self.output_folder_var, bg=c["bg_secondary"], fg=c["text_primary"], width=30,
                 anchor="w", padx=10, pady=8).pack(side="left", expand=True, fill="x")
        RoundedButton(out_row, text="Огляд", command=self.select_output_folder, bg=c["bg_tertiary"],
                      fg=c["text_primary"], hover_bg=c["border"], width=100, height=36, parent_bg=c["bg_primary"]).pack(
            side="right", padx=(10, 0))

        self.mass_gen_btn = RoundedButton(left_col, text="🚀 Розпочати масову генерацію",
                                          command=self.start_mass_generation, bg=c["primary"], fg="#FFFFFF",
                                          hover_bg=c["primary_hover"], width=300, height=45, parent_bg=c["bg_primary"])
        self.mass_gen_btn.pack(pady=(10, 0), anchor="w")

        right_col = tk.Frame(cols_frame, bg=c["bg_primary"])
        right_col.pack(side="right", fill="both", expand=True)

        tk.Label(right_col, text="Лог виконання:", bg=c["bg_primary"], fg=c["text_secondary"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))

        log_frame = tk.Frame(right_col, bg=c["border"], padx=1, pady=1)
        log_frame.pack(fill="both", expand=True, pady=(0, 15))
        self.mass_gen_log = tk.Text(log_frame, bg="#111827", fg="#10B981", font=("Consolas", 9), state="disabled",
                                    height=10)
        self.mass_gen_log.pack(fill="both", expand=True)

        self.mass_gen_progress_var = tk.DoubleVar()
        self.mass_pb = ttk.Progressbar(right_col, variable=self.mass_gen_progress_var, maximum=100)
        self.mass_pb.pack(fill="x", pady=(0, 5))
        self.mass_gen_progress_label = tk.Label(right_col, text="Готово до роботи", bg=c["bg_primary"],
                                                fg=c["text_tertiary"], font=("Segoe UI", 9))
        self.mass_gen_progress_label.pack(anchor="w")

    def select_csv_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path: self.csv_path_var.set(path)

    def select_output_folder(self):
        path = filedialog.askdirectory()
        if path: self.output_folder_var.set(path)

    def start_mass_generation(self):
        csv_path = self.csv_path_var.get()
        if not csv_path or csv_path == "Не вибрано" or not os.path.exists(csv_path):
            return messagebox.showerror("Помилка", "Виберіть дійсний CSV файл.")

        self.mass_gen_btn.config_state("disabled")
        self.mass_gen_progress_var.set(0)
        self.mass_gen_log.config(state="normal")
        self.mass_gen_log.delete(1.0, tk.END)
        self.mass_gen_log.config(state="disabled")

        threading.Thread(target=self.run_mass_generation,
                         args=(csv_path, self.mass_template_var.get(), self.output_folder_var.get()),
                         daemon=True).start()

    def run_mass_generation(self, csv_path, template_type, output_folder):
        import csv
        try:
            with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                sample = f.read(1024)
                f.seek(0)
                try:
                    detected_delimiter = csv.Sniffer().sniff(sample, delimiters=",;").delimiter
                except csv.Error:
                    detected_delimiter = ";"

                reader = csv.reader(f, delimiter=detected_delimiter)
                all_lines = list(reader)

                if not all_lines:
                    return self.root.after(0, lambda: [messagebox.showerror("Помилка", "Файл порожній."),
                                                       self.mass_gen_btn.config_state("normal")])

                fieldnames = [n.strip() for n in all_lines[0]]
                rows = [{fieldnames[i]: val.strip() for i, val in enumerate(line) if i < len(fieldnames)} for line in
                        all_lines[1:] if line and any(line)]

                def find_val(row_dict, aliases):
                    norm = [a.lower().strip().replace("'", "\u2019") for a in aliases]
                    for k, v in row_dict.items():
                        if k.lower().strip().replace("'", "\u2019") in norm: return str(v).strip()
                    return ""

                count = 0
                for idx, row in enumerate(rows):
                    if "Cyberverse" in template_type:
                        prizv = find_val(row, ["Прізвище", "Surname", "Last Name"])
                        imya = find_val(row, ["Ім'я", "Ім\u2019я", "Name", "First Name"])
                        pobat = find_val(row, ["По батькові", "Middle Name", "Patronymic"])
                        place = ("" if template_type == "Cyberverse Participation Certificate" else find_val(row,
                                                                                                             ["Місце",
                                                                                                              "Зайняте місце",
                                                                                                              "Place",
                                                                                                              "Rank"]))
                        name = f"{prizv} {imya} {pobat}".strip() or find_val(row, ["ПІБ", "Full Name", "Name"])
                        row.update({"Прізвище": prizv, "Ім'я": imya, "По батькові": pobat, "Місце": place})
                    else:
                        imya_other = row.get("Ім'я") or row.get("Ім\u2019я") or ""
                        row["Ім'я"] = imya_other
                        name = f"{row.get('Прізвище', '')} {imya_other}".strip()

                    self.root.after(0, self._update_mass_gen_progress, ((idx + 1) / len(rows) * 100), name, idx + 1,
                                    len(rows))

                    try:
                        # ВИКЛИК ОРИГІНАЛЬНОЇ ФУНКЦІЇ МАСОВОЇ ГЕНЕРАЦІЇ
                        output_file = self.system.user_workflow(template_type, row)
                        count += 1
                        self.root.after(0, self._log_mass_gen,
                                        f"✅ [{count}] {name} → {os.path.basename(output_file)}\n")
                    except Exception as e:
                        self.root.after(0, self._log_mass_gen, f"❌ Помилка для {name}: {e}\n")

                summary = f"\n{'=' * 50}\n✅ Успішно згенеровано {count} документів.\n📁 Збережено в: {output_folder}\n"
                self.root.after(0, lambda: [self._log_mass_gen(summary), self.mass_gen_btn.config_state("normal"),
                                            messagebox.showinfo("Готово", "Масове генерування завершено!")])

        except Exception as e:
            self.root.after(0, lambda: [messagebox.showerror("Помилка", f"Помилка читання CSV:\n{e}"),
                                        self.mass_gen_btn.config_state("normal")])

    def _update_mass_gen_progress(self, progress, name, idx, total):
        self.mass_gen_progress_var.set(progress)
        self.mass_gen_progress_label.config(text=f"[{idx}/{total}] Обробка: {name}...")

    def _log_mass_gen(self, message):
        self.mass_gen_log.config(state="normal")
        self.mass_gen_log.insert(tk.END, message)
        self.mass_gen_log.config(state="disabled")
        self.mass_gen_log.see(tk.END)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — VERIFY
    # ══════════════════════════════════════════════════════════════════════════
    def _build_verify_tab(self):
        c = self.colors
        container = tk.Frame(self.ver_frame, bg=c["bg_primary"], padx=40, pady=30)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="🔍 Перевірка достовірності PDF", font=("Segoe UI", 16, "bold"), bg=c["bg_primary"],
                 fg=c["text_primary"]).pack(anchor="w", pady=(0, 20))

        top_controls = tk.Frame(container, bg=c["bg_primary"])
        top_controls.pack(fill="x", pady=(0, 20))

        RoundedButton(top_controls, text="📄 Перевірити один файл", command=self.verify_single_pdf, bg=c["primary"],
                      fg="#FFFFFF", hover_bg=c["primary_hover"], width=220, height=42, parent_bg=c["bg_primary"]).pack(
            side="left", padx=(0, 15))
        RoundedButton(top_controls, text="📂 Масова перевірка (папка)", command=self.verify_folder, bg=c["bg_tertiary"],
                      fg=c["text_primary"], hover_bg=c["border"], width=240, height=42, parent_bg=c["bg_primary"]).pack(
            side="left")

        log_frame = tk.Frame(container, bg=c["border"], padx=1, pady=1)
        log_frame.pack(fill="both", expand=True)

        self.verify_log = tk.Text(log_frame, bg="#111827", fg="#F3F4F6", font=("Consolas", 10), state="disabled",
                                  wrap="word")
        self.verify_log.pack(fill="both", expand=True)

        self.ver_progress_var = tk.DoubleVar()
        self.ver_pb = ttk.Progressbar(container, variable=self.ver_progress_var, maximum=100)
        self.ver_pb.pack(fill="x", pady=(10, 5))
        self.ver_progress_label = tk.Label(container, text="Очікування файлу...", bg=c["bg_primary"],
                                           fg=c["text_tertiary"], font=("Segoe UI", 9))
        self.ver_progress_label.pack(anchor="w")

    def _log_verify(self, text, clear=False):
        self.verify_log.config(state="normal")
        if clear: self.verify_log.delete(1.0, tk.END)
        self.verify_log.insert(tk.END, text + "\n")
        self.verify_log.see(tk.END)
        self.verify_log.config(state="disabled")

    def verify_single_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not path: return

        self._log_verify(f"[*] Перевірка файлу: {os.path.basename(path)}", clear=True)
        self.ver_progress_var.set(50)
        self.ver_progress_label.config(text="Аналіз...", fg=self.colors["primary"])
        self.root.update()

        def run_single():
            import sys, io
            old = sys.stdout
            sys.stdout = buf = io.StringIO()
            try:
                # ОРИГІНАЛЬНИЙ ВИКЛИК
                self.system.admin_workflow(path)
                output = buf.getvalue()
                self.root.after(0, lambda: self._log_verify(output))
                if "VALID" in output:
                    self.root.after(0, lambda: self.ver_progress_label.config(text="✅ Документ валідний",
                                                                              fg=self.colors["success"]))
                elif "TAMPERED" in output:
                    self.root.after(0, lambda: self.ver_progress_label.config(text="❌ Документ пошкоджено",
                                                                              fg=self.colors["danger"]))
            except Exception as e:
                self.root.after(0, lambda: self._log_verify(f"[ERROR] Помилка: {str(e)}"))
            finally:
                sys.stdout = old
                self.root.after(0, lambda: self.ver_progress_var.set(100))

        threading.Thread(target=run_single, daemon=True).start()

    def verify_folder(self):
        folder = filedialog.askdirectory()
        if not folder: return

        pdf_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".pdf")]
        if not pdf_files: return messagebox.showinfo("Інфо", "PDF файлів не знайдено.")

        self._log_verify(f"[*] Масова перевірка ({len(pdf_files)} файлів)...\n", clear=True)
        threading.Thread(target=self._run_folder_verify, args=(pdf_files,), daemon=True).start()

    def _run_folder_verify(self, pdf_files):
        import sys, io
        valid, tampered, errors = 0, 0, 0
        old_diag = getattr(self.system, "diagnostic_mode", False)
        self.system.diagnostic_mode = False

        for i, path in enumerate(pdf_files):
            filename = os.path.basename(path)
            old_stdout = sys.stdout
            sys.stdout = result_io = io.StringIO()

            try:
                self.system.admin_workflow(path)
                out = result_io.getvalue()
                if "VALID" in out:
                    status, valid = "✅ VALID", valid + 1
                elif "TAMPERED" in out:
                    status, tampered = "❌ TAMPERED", tampered + 1
                else:
                    status, errors = "⚠️ ERROR", errors + 1
                log_msg = f"{filename}: {status}"
            except Exception as e:
                errors += 1
                log_msg = f"{filename}: 💥 CRITICAL ERROR ({e})"
            finally:
                sys.stdout = old_stdout

            self.root.after(0, self._update_ver_progress, ((i + 1) / len(pdf_files)) * 100, log_msg, i + 1,
                            len(pdf_files))

        self.system.diagnostic_mode = old_diag
        summary = f"\n--- Підсумок ---\nВалідних: {valid}\nПідроблених: {tampered}\nПомилок читання: {errors}"
        self.root.after(0, lambda: [self._log_verify(summary),
                                    self.ver_progress_label.config(text="✅ Перевірку завершено",
                                                                   fg=self.colors["success"])])

    def _update_ver_progress(self, progress, log_msg, idx, total):
        self.ver_progress_var.set(progress)
        self.ver_progress_label.config(text=f"Перевірка: {idx}/{total}")
        self._log_verify(log_msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = ProtectionApp(root)
    root.mainloop()