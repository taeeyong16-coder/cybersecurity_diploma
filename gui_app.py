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
        
        self.signature_path = ""
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

        # User Tab
        self.user_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.user_frame, text=" 👤 КОРИСТУВАЧ ")
        self.setup_user_tab()

        # Admin Tab
        self.admin_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.admin_frame, text=" 🛡️ АДМІНІСТРАТОР ")
        self.setup_admin_tab()

    def setup_user_tab(self):
        main_container = ttk.Frame(self.user_frame)
        main_container.pack(fill="both", expand=True, padx=30, pady=20)

        # Header
        ttk.Label(main_container, text="Генерація захищеного документа", style="Header.TLabel").pack(pady=(0, 20))

        # Template selection
        ttk.Label(main_container, text="Виберіть шаблон документа:", style="Subheader.TLabel").pack(pady=(10, 5), anchor="w")
        self.template_var = tk.StringVar(value="Cyberverse Certificate")
        templates = ["Cyberverse Certificate", "Certificate of Achievement", "Application Form", "Contract for Education"]
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

        self.fields_container = self.scrollable_frame
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

        self.render_fields()

        # Signature and Action Buttons (Outside scrollable area)
        bottom_container = ttk.Frame(main_container)
        bottom_container.pack(fill="x", pady=10)
        
        ttk.Label(bottom_container, text="Цифровий підпис:", style="Subheader.TLabel").pack(pady=(10, 5), anchor="w")
        sig_container = ttk.Frame(bottom_container, relief="groove", padding=10)
        sig_container.pack(fill="x", pady=5)
        
        self.sig_label = ttk.Label(sig_container, text="Оберіть файл підпису (PNG)", foreground="gray")
        self.sig_label.pack(side="left", padx=5)
        ttk.Button(sig_container, text="📁 Оглянути...", command=self.upload_signature).pack(side="right")

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
            
            # Додаємо обробку апострофа при отриманні даних в GUI теж (у методі generate_document)

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

    def setup_admin_tab(self):
        main_container = ttk.Frame(self.admin_frame)
        main_container.pack(fill="both", expand=True, padx=30, pady=20)

        ttk.Label(main_container, text="Верифікація документа", style="Header.TLabel").pack(pady=(0, 20))
        
        ttk.Button(main_container, text="🔍 ВИБРАТИ PDF ДЛЯ ПЕРЕВІРКИ", style="Action.TButton", command=self.verify_document).pack(pady=10, ipady=5, fill="x")
        
        ttk.Button(main_container, text="📁 ПЕРЕГЛЯНУТИ АРХІВ ДОКУМЕНТІВ", command=self.open_archive).pack(pady=5, fill="x")
        
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
        
        # Special case: Signature image
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

        if not self.signature_path:
            # Removed fallback to dummy
            missing_fields.append("Підпис (картинка)")

        if missing_fields:
            error_msg = "Будь ласка, заповніть всі поля:\n\n" + "\n".join([f"• {f}" for f in missing_fields])
            messagebox.showwarning("Заповніть всі дані", error_msg)
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

        def run_verification():
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
        threading.Thread(target=run_verification, daemon=True).start()

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ProtectionApp(root)
    root.mainloop()
