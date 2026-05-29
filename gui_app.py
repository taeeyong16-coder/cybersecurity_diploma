import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from tkcalendar import DateEntry
from main import DocumentProtectionSystem

class ProtectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система захисту PDF документів")
        self.root.geometry("900x750")
        self.root.minsize(800, 600)

        # Modern Light Theme Colors
        self.colors = {
            "bg_primary": "#FFFFFF",
            "bg_secondary": "#F5F7FA",
            "bg_tertiary": "#EEF2F7",
            "primary": "#2563EB",
            "primary_hover": "#1D4ED8",
            "success": "#10B981",
            "success_hover": "#059669",
            "danger": "#EF4444",
            "danger_hover": "#DC2626",
            "warning": "#F59E0B",
            "warning_hover": "#D97706",
            "text_primary": "#1F2937",
            "text_secondary": "#6B7280",
            "text_tertiary": "#9CA3AF",
            "border": "#E5E7EB",
            "shadow": "#00000010"
        }

        self.system = DocumentProtectionSystem()
        self.system.create_dummy_assets()

        self.bg_template_path = os.path.join("png", "background_template.png")
        
        self.create_widgets()

    def create_widgets(self):
        # Configure modern style
        self._configure_modern_styles()

        self.root.configure(background=self.colors["bg_primary"])

        # Disable tab animation at TCL level
        try:
            self.root.tk.call('set', 'tk_patchLevel')
            # Force no animation in notebook
            self.root.tk.call('option', 'add', '*Notebook.TabPadding', '12 6')
        except:
            pass

        # Create main container with padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Header section
        self._create_header(main_frame)

        # Tabs with modern styling
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill="both", padx=0, pady=0)

        # Generation Tab (formerly User)
        self.user_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.user_frame, text="  📝 ГЕНЕРУВАННЯ  ")
        self.setup_user_tab()

        # Verification Tab (formerly Admin)
        self.admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_frame, text="  🔍 ПЕРЕВІРКА  ")
        self.setup_admin_tab()

        # Mass Generation Tab
        self.mass_gen_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mass_gen_frame, text="  📦 МАССОВЕ ГЕНЕРУВАННЯ  ")
        self.setup_mass_generation_tab()

    def _configure_modern_styles(self):
        """Configure all modern styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure TFrame
        style.configure("TFrame", background=self.colors["bg_primary"], relief="flat", borderwidth=0)
        style.configure("Card.TFrame", background=self.colors["bg_primary"], relief="flat", borderwidth=1)
        style.map("Card.TFrame", background=[])

        # Configure TLabel
        style.configure("TLabel", background=self.colors["bg_primary"], foreground=self.colors["text_primary"], font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.colors["text_primary"], background=self.colors["bg_primary"])
        style.configure("Subheader.TLabel", font=("Segoe UI", 12, "bold"), foreground=self.colors["text_primary"], background=self.colors["bg_primary"])
        style.configure("Small.TLabel", font=("Segoe UI", 8), foreground=self.colors["text_secondary"], background=self.colors["bg_primary"])
        style.configure("Muted.TLabel", font=("Segoe UI", 8), foreground=self.colors["text_tertiary"], background=self.colors["bg_primary"])

        # Configure TButton - Primary Action
        style.configure("Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.colors["primary"],
            foreground="white",
            borderwidth=2,
            relief="solid",
            padding=10,
            anchor="center"
        )
        style.map("Primary.TButton",
            background=[
                ('active', self.colors["primary_hover"]),
                ('pressed', self.colors["primary_hover"]),
                ('disabled', self.colors["text_tertiary"])
            ],
            foreground=[('disabled', self.colors["bg_secondary"])]
        )

        # Configure TButton - Secondary Action
        style.configure("Secondary.TButton",
            font=("Segoe UI", 9),
            background=self.colors["bg_secondary"],
            foreground=self.colors["text_primary"],
            borderwidth=2,
            relief="solid",
            padding=8,
            anchor="center"
        )
        style.map("Secondary.TButton",
            background=[
                ('active', self.colors["bg_tertiary"]),
                ('pressed', self.colors["bg_tertiary"])
            ]
        )

        # Configure TButton - Danger Action
        style.configure("Danger.TButton",
            font=("Segoe UI", 9),
            background=self.colors["danger"],
            foreground="white",
            borderwidth=2,
            relief="solid",
            padding=8,
            anchor="center"
        )
        style.map("Danger.TButton",
            background=[
                ('active', self.colors["danger_hover"]),
                ('pressed', self.colors["danger_hover"])
            ]
        )

        # Configure TEntry - with visible borders for rounded effect
        style.configure("TEntry",
            font=("Segoe UI", 9),
            fieldbackground=self.colors["bg_primary"],
            background=self.colors["bg_primary"],
            foreground=self.colors["text_primary"],
            borderwidth=2,
            relief="solid",
            padding=6,
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"]
        )
        style.map("TEntry",
            fieldbackground=[
                ('focus', self.colors["bg_secondary"])
            ],
            borderwidth=[('focus', 2)]
        )

        # Configure TCombobox - with visible borders
        style.configure("TCombobox",
            font=("Segoe UI", 9),
            fieldbackground=self.colors["bg_primary"],
            background=self.colors["bg_primary"],
            foreground=self.colors["text_primary"],
            arrowcolor=self.colors["primary"],
            borderwidth=2,
            relief="solid",
            padding=6,
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"]
        )
        style.map("TCombobox",
            fieldbackground=[('focus', self.colors["bg_secondary"])]
        )

        # Configure TNotebook and TNotebook.Tab
        style.configure("TNotebook",
            background=self.colors["bg_primary"],
            borderwidth=0
        )
        style.configure("TNotebook.Tab",
            padding=[12, 6],
            font=("Segoe UI", 10, "bold"),
            background=self.colors["bg_secondary"],
            foreground=self.colors["text_secondary"],
            selectcolor=self.colors["bg_primary"]
        )
        # No animation - direct color switch
        style.map("TNotebook.Tab",
            background=[('selected', self.colors["bg_primary"])],
            foreground=[('selected', self.colors["primary"])],
            selectcolor=[('selected', self.colors["bg_primary"])]
        )

        # Configure Progressbar
        style.configure("TProgressbar",
            background=self.colors["success"],
            troughcolor=self.colors["bg_secondary"],
            borderwidth=0,
            relief="flat",
            thickness=8
        )

        # Configure Scrollbar
        style.configure("TScrollbar",
            background=self.colors["bg_secondary"],
            troughcolor=self.colors["bg_primary"],
            borderwidth=0,
            arrowcolor=self.colors["text_secondary"],
            darkcolor=self.colors["bg_secondary"],
            lightcolor=self.colors["bg_secondary"]
        )

    def _create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", padx=24, pady=12)

        title = ttk.Label(header_frame, text="Система захисту PDF документів", style="Header.TLabel")
        title.pack(anchor="w", pady=(0, 4))

    def _set_frame_bg(self, frame, color):
        """Helper to set frame background color"""
        style = ttk.Style()
        style.configure(f"{id(frame)}.TFrame", background=color)
        frame.configure(style=f"{id(frame)}.TFrame")

    def setup_user_tab(self):
        # Main container with two columns
        main_container = ttk.Frame(self.user_frame)
        main_container.pack(fill="both", expand=True)

        # Left column - for form content
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side="left", fill="both", expand=True)

        # Right column - for action buttons
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side="right", fill="y", padx=12, pady=12)

        # ===== LEFT COLUMN: Scrollable form =====
        canvas = tk.Canvas(left_frame, background=self.colors["bg_primary"], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Content frame with proper padding
        content_frame = ttk.Frame(self.scrollable_frame)
        content_frame.pack(fill="x", padx=20, pady=12)

        # Template selection card
        self._create_card_section(content_frame, "📋 Вибір шаблону", [
            ("Виберіть шаблон документа:", None)
        ])

        self.template_var = tk.StringVar(value="Cyberverse Certificate")
        templates = ["Cyberverse Certificate", "Cyberverse Participation Certificate", "Certificate of Achievement", "Application Form", "Contract for Education"]
        self.template_menu = ttk.Combobox(content_frame, textvariable=self.template_var, values=templates, state="readonly", font=("Segoe UI", 9))
        self.template_menu.pack(pady=(0, 16), fill="x")
        self.template_menu.bind("<<ComboboxSelected>>", self.on_template_change)

        # Fields container
        fields_label = ttk.Label(content_frame, text="📝 Персональні дані", style="Subheader.TLabel")
        fields_label.pack(pady=(0, 12), anchor="w")

        self.fields_container = ttk.Frame(content_frame)
        self.fields_container.pack(fill="x", pady=(0, 16))

        self.fields = {}
        self.course_data = {
            "Introduction to Cybersecurity": {"platform": "Cisco", "hours": "15", "level": "Beginner"},
            "Cybersecurity Essentials": {"platform": "Cisco", "hours": "30", "level": "Intermediate"},
            "Network Security": {"platform": "Cisco", "hours": "40", "level": "Advanced"},
            "Ethical Hacking (Cisco NetAcad)": {"platform": "Cisco", "hours": "70", "level": "Advanced"},
            "Google Cybersecurity Professional Certificate": {"platform": "Coursera", "hours": "180", "level": "Professional"},
            "IBM Cybersecurity Analyst": {"platform": "Coursera", "hours": "120", "level": "Intermediate"},
            "Cybersecurity Specialization (Maryland)": {"platform": "Coursera", "hours": "90", "level": "Advanced"},
            "Applied Cryptography": {"platform": "Coursera", "hours": "45", "level": "Advanced"},
        }

        self.signature_path = ""

        # Signature section
        self.sig_section = ttk.Frame(content_frame)
        self.sig_section.pack(fill="x", pady=12)

        sig_label = ttk.Label(self.sig_section, text="✍️ Цифровий підпис", style="Subheader.TLabel")
        sig_label.pack(pady=(0, 8), anchor="w")

        sig_container = ttk.Frame(self.sig_section)
        sig_container.pack(fill="x")

        self.sig_label = ttk.Label(sig_container, text="Оберіть файл підпису (PNG)", style="Small.TLabel")
        self.sig_label.pack(side="left", padx=(0, 8))
        ttk.Button(sig_container, text="📁 Вибрати...", command=self.upload_signature, style="Secondary.TButton").pack(side="left", fill="x", expand=True)

        self.render_fields()

        # ===== RIGHT COLUMN: Action Buttons =====
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill="both", expand=True)

        # Main action button
        main_btn = ttk.Button(button_frame, text="🔒 Генерувати\nта захистити\nPDF",
                             style="Primary.TButton", command=self.generate_document)
        main_btn.pack(fill="both", expand=True, pady=(0, 12))

        self.last_generated_pdf = ""

        # Open PDF button
        self.open_btn = ttk.Button(button_frame, text="📄 Відкрити\nPDF",
                                  command=self.open_pdf, state="disabled", style="Secondary.TButton")
        self.open_btn.pack(fill="both", expand=True, pady=(0, 8))

        # Open archive button
        archive_btn = ttk.Button(button_frame, text="📁 Архів\nфайлів",
                                command=self.open_archive, style="Secondary.TButton")
        archive_btn.pack(fill="both", expand=True)

    def on_template_change(self, event=None):
        self.render_fields()

    def _create_card_section(self, parent, title, fields=None):
        """Create a card section with title and optional fields"""
        card = ttk.Frame(parent)
        card.pack(fill="x", pady=(0, 24))

        label = ttk.Label(card, text=title, style="Subheader.TLabel")
        label.pack(pady=(0, 12), anchor="w")

        if fields:
            for field_label, _ in fields:
                if field_label:
                    ttk.Label(card, text=field_label, style="Small.TLabel").pack(anchor="w", pady=(4, 0))

        return card

    def render_fields(self):
        for widget in self.fields_container.winfo_children():
            widget.destroy()
        self.fields = {}

        template = self.template_var.get()

        if template == "Certificate of Achievement":
            # Course Selection
            self.add_field("Назва курсу", "combobox", list(self.course_data.keys()))
            self.add_field("Платформа", "entry", state="readonly")
            self.add_field("Кількість годин", "entry", state="readonly")
            self.add_field("Рівень курсу", "entry", state="readonly")
            
            # Auto-fill course info
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
            
            specialties = [
                "Інженерія програмного забезпечення", 
                "Комп’ютерні науки", 
                "Кібербезпека", 
                "Інформаційні системи та технології", 
                "Телекомунікації та радіотехніка"
            ]
            self.add_field("Спеціальність", "combobox", specialties)
            
            modes = ["денна", "заочна", "дистанційна"]
            self.add_field("Форма навчання", "combobox", modes)
            
        elif template == "Contract for Education":
            # self.add_field("Номер договору", "entry") # Removed for auto-generation
            self.add_field("Дата договору", "date")
            
            # Recipient
            self.add_field("Прізвище", "entry")
            self.add_field("Ім'я", "entry")
            self.add_field("По батькові", "entry")
            self.add_field("Контактний телефон", "entry")
            self.add_field("Електронна пошта", "entry")
            self.add_field("Паспорт (серія/номер) або УНЗР", "entry")

            self.add_field("Освітній рівень", "combobox", ["бакалавр", "магістр"])
            
            specialties = [
                "Інженерія програмного забезпечення", 
                "Комп’ютерні науки", 
                "Кібербезпека", 
                "Інформаційні системи та технології", 
                "Телекомунікації та радіотехніка"
            ]
            self.add_field("Спеціальність", "combobox", specialties)
            
            modes = ["денна", "заочна", "дистанційна"]
            self.add_field("Форма навчання", "combobox", modes)
            
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
            
            # Додаємо обробку апострофа при отриманні даних в GUI теж (у методі generate_document)

        # Update signature section visibility after rendering fields
        self.toggle_signature_section()

    def add_field(self, label, field_type, values=None, state="normal"):
        frame = ttk.Frame(self.fields_container)
        frame.pack(fill="x", pady=6)

        label_widget = ttk.Label(frame, text=f"{label}:", style="Small.TLabel", width=20)
        label_widget.pack(side="left", padx=(0, 12))

        if field_type == "entry":
            entry = ttk.Entry(frame, font=("Segoe UI", 10), state=state)
            entry.pack(side="right", expand=True, fill="x")
            self.fields[label] = entry
        elif field_type == "combobox":
            cb = ttk.Combobox(frame, values=values, state="readonly", font=("Segoe UI", 10))
            cb.pack(side="right", expand=True, fill="x")
            self.fields[label] = cb
        elif field_type == "date":
            de = DateEntry(frame, width=12, background=self.colors["primary"], foreground='white', borderwidth=0,
                           font=("Segoe UI", 10), date_pattern='dd.mm.yyyy')
            de.pack(side="right", expand=True, fill="x")
            self.fields[label] = de

    def update_course_info(self, event=None):
        course = self.fields["Назва курсу"].get()
        if course in self.course_data:
            info = self.course_data[course]
            for key, val in [("Платформа", info["platform"]), ("Кількість годин", info["hours"]), ("Рівень курсу", info["level"])]:
                self.fields[key].config(state="normal")
                self.fields[key].delete(0, tk.END)
                self.fields[key].insert(0, val)
                self.fields[key].config(state="readonly")

    def toggle_signature_section(self):
        """Show/hide signature section based on selected template"""
        template = self.template_var.get()
        if template in ["Cyberverse Certificate", "Cyberverse Participation Certificate"]:
            # Hide signature section ONLY for Cyberverse templates
            self.sig_section.pack_forget()
            self.signature_path = ""  # Clear signature path
            self.sig_label.config(text="Оберіть файл підпису (PNG)", foreground="gray")
        else:
            # Show signature section for all other templates (Certificate of Achievement, Application Form, Contract for Education)
            self.sig_section.pack(fill="x", pady=5)

    def setup_admin_tab(self):
        # Main container
        main_container = ttk.Frame(self.admin_frame)
        main_container.pack(fill="both", expand=True, padx=32, pady=24)

        # Title
        title = ttk.Label(main_container, text="🔐 Верифікація документів", style="Subheader.TLabel")
        title.pack(pady=(0, 24), anchor="w")

        # Mode Toggle Card
        mode_container = ttk.Frame(main_container)
        mode_container.pack(pady=(0, 24), fill="x")

        mode_label = ttk.Label(mode_container, text="Режим перевірки:", style="Small.TLabel")
        mode_label.pack(side="left", padx=(0, 16))

        self.verification_mode = tk.StringVar(value="single")
        rb1 = ttk.Radiobutton(mode_container, text="Одинична перевірка", variable=self.verification_mode, value="single")
        rb1.pack(side="left", padx=(0, 24))
        rb2 = ttk.Radiobutton(mode_container, text="Масова перевірка", variable=self.verification_mode, value="mass")
        rb2.pack(side="left")

        # Action Buttons
        ttk.Button(main_container, text="🔍 Вибрати для перевірки", style="Primary.TButton", command=self.verify_document).pack(pady=(0, 12), fill="x", ipady=4)
        ttk.Button(main_container, text="📁 Переглянути архів", command=self.open_archive, style="Secondary.TButton").pack(pady=(0, 24), fill="x")

        # Progress bar for mass verification
        self.verify_progress_var = tk.DoubleVar()
        self.verify_progress = ttk.Progressbar(main_container, variable=self.verify_progress_var, maximum=100, mode='determinate')
        self.verify_progress.pack(pady=(0, 12), fill="x")
        self.verify_progress.pack_forget()

        self.verify_progress_label = ttk.Label(main_container, text="", style="Small.TLabel")
        self.verify_progress_label.pack(pady=(0, 12))

        # Results section
        results_label = ttk.Label(main_container, text="📋 Результати перевірки:", style="Subheader.TLabel")
        results_label.pack(anchor="w", pady=(0, 12))

        self.result_text = tk.Text(main_container, height=16, state="disabled", bg=self.colors["bg_secondary"],
                                   fg=self.colors["text_primary"], font=("Consolas", 9), relief="solid",
                                   borderwidth=1, padx=12, pady=12)
        self.result_text.pack(pady=(0, 16), fill="both", expand=True)

        # Status indicator
        status_frame = ttk.Frame(main_container)
        status_frame.pack(pady=16, fill="x")

        ttk.Label(status_frame, text="Статус:", style="Small.TLabel").pack(side="left")
        self.status_label = ttk.Label(status_frame, text="⏳ Очікування...", font=("Segoe UI", 12, "bold"),
                                     foreground=self.colors["text_tertiary"])
        self.status_label.pack(side="left", padx=12)

    def upload_signature(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file_path:
            self.signature_path = file_path
            self.sig_label.config(text=os.path.basename(file_path), foreground=self.colors["success"])

    def generate_document(self):
        # 1. Collect all fields
        personal_data = {label: entry.get().strip() for label, entry in self.fields.items()}
        
        # 2. Check if all fields are filled
        missing_fields = [label for label, value in personal_data.items() if not value]

        # Special case: Signature image (only for non-Cyberverse templates)
        template = self.template_var.get()
        if template not in ["Cyberverse Certificate", "Cyberverse Participation Certificate"]:
            if not self.signature_path:
                missing_fields.append("Підпис (картинка)")

        if missing_fields:
            error_msg = "Будь ласка, заповніть всі поля:\n\n" + "\n".join([f"• {f}" for f in missing_fields])
            messagebox.showwarning("Заповніть всі дані", error_msg)
            return
        
        # Remove empty fields from dictionary (though none should be empty now)
        personal_data = {k: v for k, v in personal_data.items() if v}

        # Обробимо апостроф в імені
        if "Ім'я" in personal_data:
            personal_data["Ім'я"] = personal_data["Ім'я"].replace("’", "'")
        elif "Ім’я" in personal_data:
            val = personal_data.pop("Ім’я")
            personal_data["Ім'я"] = val.replace("’", "'")

        # Auto-generate Contract Number if applicable
        if self.template_var.get() == "Contract for Education":
            import datetime
            # Format: KNU-2026-XXXX (last 4 digits of timestamp)
            now = datetime.datetime.now()
            suffix = now.strftime("%f")[:4]
            contract_num = f"КНУ-{now.year}-{suffix}"
            personal_data["Номер договору"] = contract_num

        # Validation for Passport/UNZR
        passport_key = "Паспорт (серія/номер) або УНЗР" if "Паспорт (серія/номер) або УНЗР" in personal_data else "Номер ID"
        if passport_key in personal_data:
            passport_val = personal_data[passport_key]
            try:
                from validators import validate_passport_ua
                canonical_passport = validate_passport_ua(passport_val)
                personal_data[passport_key] = canonical_passport
            except ValueError as ve:
                messagebox.showerror("Помилка валідації документа", str(ve))
                return

        # Validation and Canonicalization of Phone Number
        if "Контактний телефон" in personal_data:
            phone_raw = personal_data["Контактний телефон"]
            try:
                from crypto_utils import CryptoManager
                canonical_phone = CryptoManager.validate_phone_ua(phone_raw)
                personal_data["Контактний телефон"] = canonical_phone
            except ValueError as ve:
                messagebox.showerror("Помилка валідації телефону", str(ve))
                return

        # Validation and Canonicalization of Payment Amount
        if self.template_var.get() == "Contract for Education":
            amount_raw = personal_data.get("Загальна вартість (грн)", "")
            try:
                from crypto_utils import CryptoManager
                canonical_amount = CryptoManager.validate_amount_ua(amount_raw)
                personal_data["Загальна вартість (грн)"] = canonical_amount
            except ValueError as ve:
                messagebox.showerror("Помилка валідації суми", str(ve))
                return

        # Remove empty fields from dictionary
        personal_data = {k: v for k, v in personal_data.items() if v}
        
        try:
            output_pdf = self.system.user_workflow(self.template_var.get(), personal_data, self.signature_path)
            self.last_generated_pdf = output_pdf
            self.open_btn.config(state="normal")
            messagebox.showinfo("Успіх", f"Захищений документ успішно створено:\n{output_pdf}")
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

    def verify_document(self):
        mode = self.verification_mode.get()

        if mode == "single":
            # Single file verification
            file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
            if not file_path:
                return

            # Візуальна індикація початку процесу
            self.status_label.config(text="⏳ ПЕРЕВІРКА...", foreground=self.colors["primary"])
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "Запуск процесу верифікації...\n")
            self.result_text.config(state="disabled")
            self.root.update_idletasks()

            def run_single_verification():
                import sys
                import io
                old_stdout = sys.stdout
                sys.stdout = mystdout = io.StringIO()

                try:
                    self.system.admin_workflow(file_path)
                    output = mystdout.getvalue()

                    # Повертаємося в головний потік для оновлення UI
                    self.root.after(0, lambda: self.update_verification_results(output))

                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Помилка", f"Помилка при верифікації:\n{e}"))
                    self.root.after(0, lambda: self.status_label.config(text="❌ ПОМИЛКА", foreground=self.colors["danger"]))
                finally:
                    sys.stdout = old_stdout

            import threading
            threading.Thread(target=run_single_verification, daemon=True).start()
            return  # Додаємо return, щоб не виконувався код масової перевірки нижче

        # Mass verification (тільки якщо mode != "single")
        folder_path = filedialog.askdirectory(title="Виберіть папку з PDF файлами")
        if not folder_path:
            return

        # Попередження для користувача, оскільки askdirectory не показує файли
        pdf_count = len([f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")])
        if pdf_count == 0:
            messagebox.showwarning("Увага", f"У вибраній папці не знайдено PDF-файлів.\nШлях: {folder_path}")
            return
            
        self.run_mass_verification(folder_path)

    def update_verification_results(self, output):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, output)
        self.result_text.config(state="disabled")
        self.result_text.see(tk.END)

        if "STATUS: VALID" in output:
            self.status_label.config(text="✅ ВАЛІДНИЙ", foreground=self.colors["success"])
        elif "STATUS: TAMPERED" in output:
            self.status_label.config(text="⚠️ ПОШКОДЖЕНИЙ", foreground=self.colors["danger"])
        else:
            self.status_label.config(text="❌ ПОМИЛКА", foreground=self.colors["warning"])

    def run_mass_verification(self, folder_path):
        import threading
        import sys
        from io import StringIO

        # Шукаємо файли незалежно від регістру розширення
        pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

        if not pdf_files:
            messagebox.showwarning("Увага", f"У папці {folder_path} не знайдено PDF файлів.")
            return

        # Show progress bar
        self.verify_progress.pack(before=self.result_text, pady=5, fill="x")
        self.verify_progress_var.set(0)

        # Reset UI
        self.status_label.config(text="⏳ МАСОВА ПЕРЕВІРКА...", foreground=self.colors["primary"])
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Знайдено {len(pdf_files)} файлів для перевірки.\n\n")
        self.result_text.config(state="disabled")

        def run_batch_verification():
            valid_count = 0
            tampered_count = 0
            error_count = 0

            # Temporarily disable diagnostic output
            old_diag = self.system.diagnostic_mode
            self.system.diagnostic_mode = False

            for i, pdf_path in enumerate(pdf_files):
                filename = os.path.basename(pdf_path)
                progress = ((i + 1) / len(pdf_files)) * 100

                # Update progress
                self.root.after(0, lambda p=progress, f=filename, idx=i+1: self._update_mass_verify_progress(p, f, idx, len(pdf_files)))

                # Capture stdout
                old_stdout = sys.stdout
                sys.stdout = result_io = StringIO()

                try:
                    self.system.admin_workflow(pdf_path)
                    sys.stdout = old_stdout
                    result_output = result_io.getvalue()

                    if "[RESULT] STATUS: VALID" in result_output:
                        status = "✅ VALID"
                        valid_count += 1
                    elif "TAMPERED" in result_output:
                        status = "❌ TAMPERED"
                        tampered_count += 1
                    elif "UNSIGNED" in result_output:
                        status = "⚠️ UNSIGNED"
                        error_count += 1
                    else:
                        status = "❓ UNKNOWN"
                        error_count += 1

                    self.root.after(0, lambda fn=filename, st=status: self._append_verify_result(fn, st))

                except Exception as e:
                    sys.stdout = old_stdout
                    error_count += 1
                    self.root.after(0, lambda fn=filename, err=str(e): self._append_verify_result(fn, f"💥 ERROR: {err}"))

            self.system.diagnostic_mode = old_diag

            # Show summary
            summary = f"\n{'='*50}\n--- Підсумок перевірки ---\n"
            summary += f"Всього файлів: {len(pdf_files)}\n"
            summary += f"Валідних:      {valid_count}\n"
            summary += f"Пошкоджених:   {tampered_count}\n"
            summary += f"Інші (помилки): {error_count}\n"

            self.root.after(0, lambda s=summary: self._finish_mass_verification(s, valid_count, tampered_count, error_count, len(pdf_files)))

        threading.Thread(target=run_batch_verification, daemon=True).start()

    def _update_mass_verify_progress(self, progress, filename, idx, total):
        self.verify_progress_var.set(progress)
        self.verify_progress_label.config(text=f"[{idx}/{total}] Перевірка: {filename}...")

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

        # Hide progress bar
        self.verify_progress.pack_forget()
        self.verify_progress_label.config(text="")

        # Update status
        if error == 0 and tampered == 0 and valid == total:
            self.status_label.config(text="✅ ВСІ ВАЛІДНІ", foreground=self.colors["success"])
        elif tampered > 0:
            self.status_label.config(text=f"⚠️ ЗНАЙДЕНО ПОШКОДЖЕНІ ({tampered})", foreground=self.colors["danger"])
        else:
            self.status_label.config(text=f"✅ ПЕРЕВІРЕНО ({valid}/{total})", foreground=self.colors["warning"])

    def setup_mass_generation_tab(self):
        # Main container
        main_container = ttk.Frame(self.mass_gen_frame)
        main_container.pack(fill="both", expand=True, padx=32, pady=24)

        # Title
        title = ttk.Label(main_container, text="📦 Масове генерування документів", style="Subheader.TLabel")
        title.pack(pady=(0, 24), anchor="w")

        # Template selection card
        template_label = ttk.Label(main_container, text="Шаблон документа:", style="Small.TLabel")
        template_label.pack(pady=(0, 8), anchor="w")

        self.mass_template_var = tk.StringVar(value="Cyberverse Certificate")
        templates = ["Cyberverse Certificate", "Cyberverse Participation Certificate"]
        ttk.Combobox(main_container, textvariable=self.mass_template_var, values=templates, state="readonly", font=("Segoe UI", 10)).pack(pady=(0, 24), fill="x")

        # CSV file selection
        csv_label = ttk.Label(main_container, text="📄 Вибір CSV файлу:", style="Small.TLabel")
        csv_label.pack(pady=(0, 8), anchor="w")

        self.csv_path_var = tk.StringVar(value="")
        csv_path_frame = ttk.Frame(main_container)
        csv_path_frame.pack(fill="x", pady=(0, 24))

        self.csv_label = ttk.Label(csv_path_frame, textvariable=self.csv_path_var, foreground=self.colors["text_tertiary"],
                                  relief="solid", padding=8, background=self.colors["bg_secondary"])
        self.csv_label.pack(side="left", expand=True, fill="x", padx=(0, 8))
        ttk.Button(csv_path_frame, text="📁 Вибрати", command=self.select_csv_file, style="Secondary.TButton").pack(side="right", fill="x", expand=True)

        # Output folder selection
        output_label = ttk.Label(main_container, text="📁 Папка призначення:", style="Small.TLabel")
        output_label.pack(pady=(0, 8), anchor="w")

        self.output_folder_var = tk.StringVar(value="generated_archive")
        output_path_frame = ttk.Frame(main_container)
        output_path_frame.pack(fill="x", pady=(0, 24))

        ttk.Entry(output_path_frame, textvariable=self.output_folder_var, font=("Segoe UI", 10), state="readonly").pack(side="left", expand=True, fill="x", padx=(0, 8))
        ttk.Button(output_path_frame, text="📁 Змінити", command=self.select_output_folder, style="Secondary.TButton").pack(side="right", fill="x", expand=True)

        # Progress bar
        self.mass_gen_progress_var = tk.DoubleVar()
        self.mass_gen_progress = ttk.Progressbar(main_container, variable=self.mass_gen_progress_var, maximum=100, mode='determinate')
        self.mass_gen_progress.pack(pady=(0, 8), fill="x")
        self.mass_gen_progress.pack_forget()

        self.mass_gen_progress_label = ttk.Label(main_container, text="", style="Small.TLabel")
        self.mass_gen_progress_label.pack(pady=(0, 16))

        # Start button
        self.mass_gen_btn = ttk.Button(main_container, text="🚀 Почати масове генерування", style="Primary.TButton", command=self.start_mass_generation)
        self.mass_gen_btn.pack(pady=(0, 24), fill="x", ipady=4)

        # Log area
        log_label = ttk.Label(main_container, text="📋 Лог процесу:", style="Small.TLabel")
        log_label.pack(anchor="w", pady=(0, 8))

        self.mass_gen_log = tk.Text(main_container, height=12, state="disabled", bg=self.colors["bg_secondary"],
                                   fg=self.colors["text_primary"], font=("Consolas", 9), relief="solid",
                                   borderwidth=1, padx=12, pady=12)
        self.mass_gen_log.pack(pady=(0, 16), fill="both", expand=True)

        ttk.Button(main_container, text="📁 Відкрити папку з файлами", command=self.open_archive, style="Secondary.TButton").pack(fill="x")

    def select_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            self.csv_path_var.set(file_path)
            self.csv_label.config(foreground=self.colors["success"])

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Виберіть папку призначення")
        if folder_path:
            self.output_folder_var.set(folder_path)

    def start_mass_generation(self):
        csv_path = self.csv_path_var.get()
        template_type = self.mass_template_var.get()
        output_folder = self.output_folder_var.get()

        if not csv_path:
            messagebox.showwarning("Увага", "Будь ласка, виберіть CSV файл з даними.")
            return

        if not os.path.exists(csv_path):
            messagebox.showerror("Помилка", f"Файл {csv_path} не знайдено.")
            return

        # Disable button during generation
        self.mass_gen_btn.config(state="disabled")

        # Reset UI
        self.mass_gen_log.config(state="normal")
        self.mass_gen_log.delete("1.0", tk.END)
        self.mass_gen_log.insert(tk.END, f"Початок масового генерування...\nШаблон: {template_type}\n\n")
        self.mass_gen_log.config(state="disabled")

        self.mass_gen_progress_var.set(0)

        import threading
        threading.Thread(target=self.run_mass_generation, args=(csv_path, template_type, output_folder), daemon=True).start()

    def run_mass_generation(self, csv_path, template_type, output_folder):
        import csv

        try:
            with open(csv_path, mode='r', encoding='utf-8-sig') as f:
                # Automatic delimiter detection
                sample = f.read(1024)
                f.seek(0)
                try:
                    detected_delimiter = csv.Sniffer().sniff(sample, delimiters=',;').delimiter
                except csv.Error:
                    detected_delimiter = ';'

                reader = csv.reader(f, delimiter=detected_delimiter)
                all_lines = list(reader)

                if not all_lines:
                    self.root.after(0, lambda: messagebox.showerror("Помилка", f"Файл {csv_path} порожній."))
                    self.root.after(0, lambda: self.mass_gen_btn.config(state="normal"))
                    return

                # Clean headers
                fieldnames = [name.strip() for name in all_lines[0]]

                rows = []
                for line in all_lines[1:]:
                    if not line or not any(line):
                        continue
                    row = {}
                    for i, val in enumerate(line):
                        if i < len(fieldnames):
                            row[fieldnames[i]] = val.strip()
                    rows.append(row)

                self.root.after(0, lambda fn=', '.join(fieldnames), d=detected_delimiter: self._log_mass_gen(f"Знайдено полів: {fn} (Роздільник: '{d}')\n"))

                count = 0
                total = len(rows)

                def find_val(row_dict, aliases):
                    norm_aliases = [a.lower().strip().replace("'", "'") for a in aliases]
                    for k, v in row_dict.items():
                        if k.lower().strip().replace("'", "'") in norm_aliases:
                            return str(v).strip()
                    return ""

                for idx, row in enumerate(rows):
                    if "Cyberverse" in template_type:
                        prizv = find_val(row, ['Прізвище', 'Surname', 'Last Name'])
                        imya = find_val(row, ['Ім\'я', "Ім\'я", 'Name', 'First Name'])
                        pobat = find_val(row, ['По батькові', 'Middle Name', 'Patronymic'])

                        if template_type == "Cyberverse Participation Certificate":
                            place = ""
                        else:
                            place = find_val(row, ['Місце', 'Зайняте місце', 'Place', 'Rank'])

                        name = f"{prizv} {imya} {pobat}".strip()
                        if not name:
                            name = find_val(row, ["ПІБ", "Full Name", "Name"])

                        row['Прізвище'] = prizv
                        row["Ім'я"] = imya
                        row['По батькові'] = pobat
                        row['Місце'] = place
                    else:
                        imya_other = row.get('Ім\'я') or row.get("Ім'я") or ""
                        row["Ім'я"] = imya_other
                        name = f"{row.get('Прізвище', '')} {imya_other}".strip()

                    progress = ((idx + 1) / total) * 100
                    self.root.after(0, lambda p=progress, n=name, i=idx+1, t=total: self._update_mass_gen_progress(p, n, i, t))

                    try:
                        output_file = self.system.user_workflow(template_type, row)
                        count += 1
                        self.root.after(0, lambda n=name, f=os.path.basename(output_file): self._log_mass_gen(f"✅ [{count}] {n} → {f}\n"))
                    except Exception as e:
                        self.root.after(0, lambda n=name, err=str(e): self._log_mass_gen(f"❌ Помилка для {n}: {err}\n"))

                summary = f"\n{'='*50}\n✅ Успішно згенеровано {count} документів.\n📁 Файли збережено в папці: {output_folder}\n"
                self.root.after(0, lambda s=summary: self._finish_mass_generation(s))

        except Exception as e:
            self.root.after(0, lambda err=str(e): messagebox.showerror("Помилка", f"Помилка при читанні CSV:\n{err}"))
            self.root.after(0, lambda: self.mass_gen_btn.config(state="normal"))

    def _update_mass_gen_progress(self, progress, name, idx, total):
        self.mass_gen_progress_var.set(progress)
        self.mass_gen_progress_label.config(text=f"[{idx}/{total}] Обробка: {name}...")

    def _log_mass_gen(self, message):
        self.mass_gen_log.config(state="normal")
        self.mass_gen_log.insert(tk.END, message)
        self.mass_gen_log.config(state="disabled")
        self.mass_gen_log.see(tk.END)

    def _finish_mass_generation(self, summary):
        self._log_mass_gen(summary)
        self.mass_gen_btn.config(state="normal")
        self.mass_gen_progress_label.config(text="✅ Завершено!")
        messagebox.showinfo("Успіх", "Масове генерування завершено успішно!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProtectionApp(root)
    root.mainloop()
