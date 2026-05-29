import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from main import DocumentProtectionSystem

class ProtectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hybrid PDF Protection System")
        self.root.geometry("700x850")
        
        self.system = DocumentProtectionSystem()
        # For demonstration, ensure dummy assets exist
        self.system.create_dummy_assets()

        self.bg_template_path = os.path.join("png", "background_template.png")
        
        self.create_widgets()

    def create_widgets(self):
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam') # Using a slightly more modern theme than default
        
        # Colors
        bg_color = "#f0f2f5"
        accent_color = "#4a90e2"
        text_color = "#333333"
        
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=text_color, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#1a2b3c", background=bg_color)
        style.configure("Subheader.TLabel", font=("Segoe UI", 12, "bold"), foreground="#2c3e50", background=bg_color)
        
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), background=accent_color, foreground="white")
        style.map("Action.TButton", background=[('active', '#357abd')])
        
        style.configure("TNotebook", background=bg_color)
        style.configure("TNotebook.Tab", padding=[20, 10], font=("Segoe UI", 10, "bold"))

        self.root.configure(background=bg_color)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=15, pady=15)

        # Generation Tab (formerly User)
        self.user_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.user_frame, text=" 📝 ГЕНЕРУВАННЯ ")
        self.setup_user_tab()

        # Verification Tab (formerly Admin)
        self.admin_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.admin_frame, text=" 🔍 ПЕРЕВІРКА ")
        self.setup_admin_tab()

        # Mass Generation Tab
        self.mass_gen_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.mass_gen_frame, text=" 📦 МАСОВЕ ГЕНЕРУВАННЯ ")
        self.setup_mass_generation_tab()

    def setup_user_tab(self):
        main_container = ttk.Frame(self.user_frame)
        main_container.pack(fill="both", expand=True, padx=30, pady=20)

        # Header
        ttk.Label(main_container, text="Генерація захищеного документа", style="Header.TLabel").pack(pady=(0, 20))

        # Template selection
        ttk.Label(main_container, text="Виберіть шаблон документа:", style="Subheader.TLabel").pack(pady=(10, 5), anchor="w")
        self.template_var = tk.StringVar(value="Cyberverse Certificate")
        templates = ["Cyberverse Certificate", "Cyberverse Participation Certificate", "Certificate of Achievement", "Application Form", "Contract for Education"]
        self.template_menu = ttk.Combobox(main_container, textvariable=self.template_var, values=templates, state="readonly", font=("Segoe UI", 10))
        self.template_menu.pack(pady=5, fill="x")
        self.template_menu.bind("<<ComboboxSelected>>", self.on_template_change)

        # Scrollable container for fields
        canvas = tk.Canvas(main_container, background="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=600)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create a separate frame for fields only (will be cleared on template change)
        self.fields_container = ttk.Frame(self.scrollable_frame)
        self.fields_container.pack(fill="x", pady=5)

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

        # Signature container (inside scrollable area but separate from fields_container - will be shown/hidden based on template)
        self.sig_section = ttk.Frame(self.scrollable_frame)
        self.sig_section.pack(fill="x", pady=15)

        ttk.Label(self.sig_section, text="Цифровий підпис:", style="Subheader.TLabel").pack(pady=(10, 5), anchor="w")
        sig_container = ttk.Frame(self.sig_section, relief="groove", padding=10)
        sig_container.pack(fill="x", pady=5)
        
        self.sig_label = ttk.Label(sig_container, text="Оберіть файл підпису (PNG)", foreground="gray")
        self.sig_label.pack(side="left", padx=5)
        ttk.Button(sig_container, text="📁 Оглянути...", command=self.upload_signature).pack(side="right")

        self.render_fields()

        # Action Buttons (Outside scrollable area)
        bottom_container = ttk.Frame(main_container)
        bottom_container.pack(fill="x", pady=10)

        ttk.Button(bottom_container, text="🔒 ЗГЕНЕРУВАТИ ТА ЗАХИСТИТИ PDF", style="Action.TButton", command=self.generate_document).pack(pady=10, ipady=10, fill="x")

        self.last_generated_pdf = ""
        self.open_btn = ttk.Button(bottom_container, text="📄 ВІДКРИТИ СТВОРЕНИЙ PDF", command=self.open_pdf, state="disabled")
        self.open_btn.pack(pady=2, fill="x")

        ttk.Button(bottom_container, text="📁 ВІДКРИТИ АРХІВ ЗГЕНЕРОВАНИХ ФАЙЛІВ", command=self.open_archive).pack(pady=5, fill="x")

    def on_template_change(self, event=None):
        self.render_fields()

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
        frame.pack(fill="x", pady=5)
        ttk.Label(frame, text=f"{label}:", width=20).pack(side="left")
        
        if field_type == "entry":
            entry = ttk.Entry(frame, font=("Segoe UI", 10), state=state)
            entry.pack(side="right", expand=True, fill="x")
            self.fields[label] = entry
        elif field_type == "combobox":
            cb = ttk.Combobox(frame, values=values, state="readonly", font=("Segoe UI", 10))
            cb.pack(side="right", expand=True, fill="x")
            self.fields[label] = cb
        elif field_type == "date":
            de = DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2, 
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
        main_container = ttk.Frame(self.admin_frame)
        main_container.pack(fill="both", expand=True, padx=30, pady=20)

        ttk.Label(main_container, text="Верифікація документа", style="Header.TLabel").pack(pady=(0, 20))

        # Mode Toggle: Single vs Mass Verification
        mode_container = ttk.Frame(main_container, relief="groove", padding=10)
        mode_container.pack(pady=(0, 15), fill="x")

        ttk.Label(mode_container, text="Режим перевірки:", style="Subheader.TLabel").pack(side="left", padx=(0, 10))

        self.verification_mode = tk.StringVar(value="single")
        ttk.Radiobutton(mode_container, text="Одинична перевірка", variable=self.verification_mode, value="single").pack(side="left", padx=10)
        ttk.Radiobutton(mode_container, text="Масова перевірка", variable=self.verification_mode, value="mass").pack(side="left", padx=10)

        # Action buttons
        ttk.Button(main_container, text="🔍 ВИБРАТИ ДЛЯ ПЕРЕВІРКИ", style="Action.TButton", command=self.verify_document).pack(pady=10, ipady=5, fill="x")

        ttk.Button(main_container, text="📁 ПЕРЕГЛЯНУТИ АРХІВ ДОКУМЕНТІВ", command=self.open_archive).pack(pady=5, fill="x")

        # Progress bar for mass verification
        self.verify_progress_var = tk.DoubleVar()
        self.verify_progress = ttk.Progressbar(main_container, variable=self.verify_progress_var, maximum=100, mode='determinate')
        self.verify_progress.pack(pady=5, fill="x")
        self.verify_progress.pack_forget()  # Hide initially

        self.verify_progress_label = ttk.Label(main_container, text="", foreground="#4a90e2")
        self.verify_progress_label.pack(pady=2)

        ttk.Label(main_container, text="Лог процесу:", style="Subheader.TLabel").pack(anchor="w", pady=(20, 5))
        self.result_text = tk.Text(main_container, height=15, state="disabled", bg="white", font=("Consolas", 10), relief="flat", padx=10, pady=10)
        self.result_text.pack(pady=5, fill="both", expand=True)
        
        self.status_container = ttk.Frame(main_container, relief="flat", padding=10)
        self.status_container.pack(pady=20, fill="x")
        
        ttk.Label(self.status_container, text="РЕЗУЛЬТАТ ПЕРЕВІРКИ: ", font=("Segoe UI", 12, "bold")).pack(side="left")
        self.status_label = ttk.Label(self.status_container, text="Очікування", font=("Segoe UI", 14, "bold"), foreground="gray")
        self.status_label.pack(side="left", padx=10)

    def upload_signature(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file_path:
            self.signature_path = file_path
            self.sig_label.config(text=os.path.basename(file_path), foreground="#2ecc71")

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
            self.status_label.config(text="⏳ ПЕРЕВІРКА...", foreground="#3498db")
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
                    self.root.after(0, lambda: self.status_label.config(text="❌ ERROR", foreground="#e74c3c"))
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
            self.status_label.config(text="✅ VALID", foreground="#27ae60")
        elif "STATUS: TAMPERED" in output:
            self.status_label.config(text="⚠️ TAMPERED", foreground="#e74c3c")
        else:
            self.status_label.config(text="❌ INVALID", foreground="#f39c12")

    def run_mass_verification(self, folder_path):
        import glob
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
        self.status_label.config(text="⏳ МАСОВА ПЕРЕВІРКА...", foreground="#3498db")
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
            self.status_label.config(text="✅ ВСІ ВАЛІДНІ", foreground="#27ae60")
        elif tampered > 0:
            self.status_label.config(text=f"⚠️ ЗНАЙДЕНО ПОШКОДЖЕНІ ({tampered})", foreground="#e74c3c")
        else:
            self.status_label.config(text=f"✅ ПЕРЕВІРЕНО ({valid}/{total})", foreground="#f39c12")

    def setup_mass_generation_tab(self):
        main_container = ttk.Frame(self.mass_gen_frame)
        main_container.pack(fill="both", expand=True, padx=30, pady=20)

        ttk.Label(main_container, text="Масове генерування документів", style="Header.TLabel").pack(pady=(0, 20))

        # Template selection
        ttk.Label(main_container, text="Виберіть шаблон документа:", style="Subheader.TLabel").pack(pady=(10, 5), anchor="w")
        self.mass_template_var = tk.StringVar(value="Cyberverse Certificate")
        templates = ["Cyberverse Certificate", "Cyberverse Participation Certificate"]
        ttk.Combobox(main_container, textvariable=self.mass_template_var, values=templates, state="readonly", font=("Segoe UI", 10)).pack(pady=5, fill="x")

        # CSV file selection
        csv_container = ttk.Frame(main_container, relief="groove", padding=10)
        csv_container.pack(pady=15, fill="x")

        ttk.Label(csv_container, text="Файл CSV з даними:", style="Subheader.TLabel").pack(anchor="w", pady=(0, 5))
        self.csv_path_var = tk.StringVar(value="")
        csv_path_frame = ttk.Frame(csv_container)
        csv_path_frame.pack(fill="x", pady=5)

        self.csv_label = ttk.Label(csv_path_frame, textvariable=self.csv_path_var, foreground="gray", relief="sunken", padding=5)
        self.csv_label.pack(side="left", expand=True, fill="x", padx=(0, 10))
        ttk.Button(csv_path_frame, text="📁 Вибрати CSV...", command=self.select_csv_file).pack(side="right")

        # Output folder selection (optional)
        output_container = ttk.Frame(main_container, relief="groove", padding=10)
        output_container.pack(pady=15, fill="x")

        ttk.Label(output_container, text="Папка призначення (за замовчуванням: generated_archive):", style="Subheader.TLabel").pack(anchor="w", pady=(0, 5))
        self.output_folder_var = tk.StringVar(value="generated_archive")
        output_path_frame = ttk.Frame(output_container)
        output_path_frame.pack(fill="x", pady=5)

        ttk.Entry(output_path_frame, textvariable=self.output_folder_var, font=("Segoe UI", 10), state="readonly").pack(side="left", expand=True, fill="x", padx=(0, 10))
        ttk.Button(output_path_frame, text="📁 Змінити...", command=self.select_output_folder).pack(side="right")

        # Progress bar
        self.mass_gen_progress_var = tk.DoubleVar()
        self.mass_gen_progress = ttk.Progressbar(main_container, variable=self.mass_gen_progress_var, maximum=100, mode='determinate')
        self.mass_gen_progress.pack(pady=10, fill="x")

        self.mass_gen_progress_label = ttk.Label(main_container, text="", foreground="#4a90e2")
        self.mass_gen_progress_label.pack(pady=2)

        # Start button
        self.mass_gen_btn = ttk.Button(main_container, text="🚀 ПОЧАТИ МАСОВЕ ГЕНЕРУВАННЯ", style="Action.TButton", command=self.start_mass_generation)
        self.mass_gen_btn.pack(pady=15, ipady=10, fill="x")

        # Log area
        ttk.Label(main_container, text="Лог процесу:", style="Subheader.TLabel").pack(anchor="w", pady=(10, 5))
        self.mass_gen_log = tk.Text(main_container, height=12, state="disabled", bg="white", font=("Consolas", 9), relief="flat", padx=10, pady=10)
        self.mass_gen_log.pack(pady=5, fill="both", expand=True)

        ttk.Button(main_container, text="📁 ВІДКРИТИ ПАПКУ З ФАЙЛАМИ", command=self.open_archive).pack(pady=5, fill="x")

    def select_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            self.csv_path_var.set(file_path)
            self.csv_label.config(foreground="#27ae60")

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
