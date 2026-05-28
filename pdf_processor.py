import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import io
import os

class PDFProcessor:
    """
    Handles PDF generation with steganographic background 
    and extraction of text/images for verification.
    """

    def __init__(self):
        # Register a Unicode font to support Cyrillic characters
        # Try to find a common system font, or fall back to Helvetica (which might fail for Cyrillic)
        self.font_name = "Helvetica"
        self.font_bold = "Helvetica-Bold"
        
        # Paths to search for fonts on Windows
        font_paths = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\tahoma.ttf"
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont('UnicodeFont', path))
                    # Also register bold version if available
                    bold_path = path.replace(".ttf", "bd.ttf")
                    if os.path.exists(bold_path):
                        pdfmetrics.registerFont(TTFont('UnicodeFontBold', bold_path))
                        self.font_bold = 'UnicodeFontBold'
                    else:
                        self.font_bold = 'UnicodeFont'
                        
                    self.font_name = 'UnicodeFont'
                    break
                except:
                    continue

        # Register monospaced font for Cyrillic support
        self.font_mono = "Courier" # Fallback
        mono_paths = [
            r"C:\Windows\Fonts\cour.ttf", # Courier New
            r"C:\Windows\Fonts\consola.ttf", # Consolas
            r"C:\Windows\Fonts\lucon.ttf" # Lucida Console
        ]
        for path in mono_paths:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont('UnicodeMono', path))
                    self.font_mono = 'UnicodeMono'
                    break
                except:
                    continue

    def generate_pdf(self, output_path: str, template_type: str, data: dict, 
                     stego_bg: Image.Image, user_signature_path: str = None):
        """Generates a protected PDF using a unified drawing method."""
        from reportlab.lib.pagesizes import letter, landscape
        
        if "Cyberverse" in template_type:
            # Reverting to landscape (album) as requested by user
            pagesize = landscape(letter)
        else:
            pagesize = letter
            
        c = canvas.Canvas(output_path, pagesize=pagesize)
        width, height = pagesize

        # 1. Insert Steganographic Background
        bg_buffer = io.BytesIO()
        stego_bg.save(bg_buffer, format='PNG')
        bg_buffer.seek(0)
        c.drawImage(ImageReader(bg_buffer), 0, 0, width=width, height=height)

        # Ensure Cyberverse is recognizable by text layer
        # Draw this as VERY small/transparent text behind/on background
        if "Cyberverse" in template_type:
            c.saveState()
            c.setFont(self.font_name, 1)
            c.setFillColorRGB(0, 0, 0, 0.001)
            # Use specific name for identification during extraction
            c.drawString(width/2, 10, template_type.upper())
            c.restoreState()

        # 2. Render visible text using unified method
        self._draw_document(c, width, height, template_type, data)

        if "Cyberverse" in template_type:
            return c.save()

        # 3. Insert User Signature Image if provided
        if user_signature_path and os.path.exists(user_signature_path) and "Cyberverse" not in template_type:
            sig_pos = self._get_asset_position(template_type, "signature", width, height)
            c.drawImage(user_signature_path, sig_pos['x'], sig_pos['y'], 
                        width=sig_pos['w'], height=sig_pos['h'], mask='auto')

        # 4. Insert Official Stamp if applicable
        stamp_path = os.path.join("png", "stamp.png")
        if os.path.exists(stamp_path) and "Cyberverse" not in template_type:
            stamp_pos = self._get_asset_position(template_type, "stamp", width, height)
            if stamp_pos:
                c.drawImage(stamp_path, stamp_pos['x'], stamp_pos['y'], 
                            width=stamp_pos['w'], height=stamp_pos['h'], mask='auto')

        c.save()

    def _get_asset_position(self, template_type, asset_type, width, height):
        """Unified helper for asset (signature/stamp) positioning."""
        if asset_type == "signature":
            if template_type == "Certificate of Achievement":
                return {'x': 150, 'y': getattr(self, "last_y", 195), 'w': 120, 'h': 40}
            elif template_type == "Application Form":
                return {'x': 150, 'y': 130, 'w': 120, 'h': 40}
            elif template_type == "Contract for Education":
                return {'x': 70, 'y': getattr(self, "last_y", 70), 'w': 120, 'h': 40}
            else: # Official Letter or others
                return {'x': 100, 'y': 150, 'w': 120, 'h': 40}
        
        elif asset_type == "stamp":
            if template_type == "Certificate of Achievement":
                return {'x': width - 220, 'y': getattr(self, "last_y", 190), 'w': 100, 'h': 100}
            elif template_type == "Application Form":
                return {'x': width - 230, 'y': getattr(self, "last_y", 120), 'w': 100, 'h': 100}
            elif template_type == "Contract for Education":
                return {'x': width - 250, 'y': getattr(self, "last_y", 40), 'w': 100, 'h': 100}
            elif template_type == "Official Letter":
                return {'x': width - 200, 'y': 100, 'w': 100, 'h': 100}
        return None

    def _draw_document(self, c, width, height, template_type, data):
        """Universal method for drawing all document types based on template configurations."""
        if template_type == "Certificate of Achievement":
            self._draw_certificate(c, width, height, data)
            self.last_y = getattr(self, "last_cert_y", 190)
        elif template_type == "Contract for Education":
            self._draw_contract(c, width, height, data)
            self.last_y = getattr(self, "last_contract_y", 75)
        elif template_type == "Official Letter":
            self._draw_letter(c, width, height, data)
            self.last_y = 150 # Fixed for letter
        elif "Cyberverse" in template_type:
            # self.last_y = 100 # Resetting to default not needed if _draw_cyberverse handles it
            self._draw_cyberverse(c, width, height, data, template_type)
        else: # Application Form
            self._draw_application(c, width, height, data)
            self.last_y = getattr(self, "last_app_y", 100)

    def _draw_certificate(self, c, width, height, data):
        # Background adjustments for better text placement (optional crop/resize happens at drawImage)
        
        # Header
        c.setFont(self.font_bold, 24) 
        c.setStrokeColorRGB(0.5, 0.4, 0.2)
        c.setFillColorRGB(0.4, 0.3, 0.1)
        c.drawCentredString(width / 2, height - 250, "СЕРТИФІКАТ") 
        
        c.setFont(self.font_name, 11) 
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawCentredString(width / 2, height - 265, "ПРО УСПІШНЕ ЗАВЕРШЕННЯ КУРСУ") 

        # Main Course Info
        # Зменшено відступ між заголовком та назвою курсу
        y_pos = height - 285 
        course_name = data.get("Назва курсу", "")
        c.setFont(self.font_bold, 14) 
        c.drawCentredString(width / 2, y_pos, f"\"{course_name}\"")
        
        y_pos -= 20
        c.setFont(self.font_name, 10) 
        c.drawCentredString(width / 2, y_pos, f"Організатор/Платформа: {data.get('Платформа', '')}")
        y_pos -= 12
        c.drawCentredString(width / 2, y_pos, f"Обсяг: {data.get('Кількість годин', '')} год. | Рівень: {data.get('Рівень курсу', '')}")

        # Recipient Info
        # Прибрано зайві відступи між інформацією про курс та ім'ям
        y_pos -= 30 
        c.setFont(self.font_name, 11) 
        c.drawCentredString(width / 2, y_pos, "Цей сертифікат свідчить про те, що")
        y_pos -= 25 
        
        last_name = data.get("Прізвище", "")
        first_name = data.get("Ім'я", "")
        middle_name = data.get("По батькові", "")
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        
        c.setFont(self.font_bold, 20) 
        c.drawCentredString(width / 2, y_pos, full_name)
        
        y_pos -= 20 
        c.setFont(self.font_name, 9) 
        c.drawCentredString(width / 2, y_pos, f"Студентський квиток №: {data.get('Номер студентського', '')}")
        
        y_pos -= 12 
        c.drawCentredString(width / 2, y_pos, f"Дата завершення: {data.get('Дата завершення', '')}")

        # University Info
        # Прибрано зайві абзаци між датою та університетом
        y_pos -= 20 
        c.setFont(self.font_bold, 9) 
        c.drawCentredString(width / 2, y_pos, "Київський національний університет імені Тараса Шевченка")
        y_pos -= 12
        c.setFont(self.font_name, 8) 
        c.drawCentredString(width / 2, y_pos, "Факультет інформаційних технологій")
        
        # Responsible Person / Signatures area
        y_pos -= 100 # Increased gap between text and signatures
        c.setFillColorRGB(0, 0, 0) # Set color to black for signatures
        c.setStrokeColorRGB(0, 0, 0) # Set line color to black
        c.setFont(self.font_bold, 9)
        c.drawString(130, y_pos, "Підпис клієнта:")
        c.line(130, y_pos - 2, 250, y_pos - 2)
        
        c.drawString(width - 290, y_pos, "Директор:")
        c.setFont(self.font_name, 9)
        c.drawString(width - 230, y_pos, "Прищепа О.О.")
        c.line(width - 235, y_pos - 2, width - 120, y_pos - 2)
        
        # Add labels for signatures
        c.setFont(self.font_name, 7)
        c.drawString(width - 200, y_pos - 10, "(підпис директора)")
        c.drawString(150, y_pos - 10, "(підпис клієнта)") # Ensure client signature label is also black and visible

        # Update signature/stamp positions in generate_pdf if needed
        self.last_cert_y = y_pos

        # Reset color for any potential later drawing (though this is the end of certificate)
        c.setFillColorRGB(0, 0, 0)

    def _draw_cyberverse(self, c, width, height, data, template_type="Cyberverse Certificate"):
        """Малювання сертифіката Cyberverse на спеціальному фоні."""
        # Гнучкий пошук полів у словнику (ігноруючи регістр, пробіли та різні апострофи)
        def get_field(aliases):
            for k, v in data.items():
                k_norm = str(k).lower().strip().replace("’", "'")
                for a in aliases:
                    if a.lower().strip().replace("’", "'") == k_norm:
                        return str(v).strip()
            return ""

        last_name = get_field(["Прізвище", "Last Name", "Surname"])
        first_name = get_field(["Ім'я", "Ім’я", "First Name", "Name"])
        middle_name = get_field(["По батькові", "Middle Name", "Patronymic"])
        
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        
        # Якщо окремі поля порожні, спробуємо взяти ПІБ цілком
        if not full_name:
            full_name = get_field(["ПІБ", "Full Name", "Participant", "Name"])

        # 1. ПІБ: чорним кольором, центр сторінки по горизонталі
        c.setFillColorRGB(0, 0, 0)
        
        # Використовуємо моноширинний шрифт для шаблону участі
        if template_type == "Cyberverse Participation Certificate":
            c.setFont(self.font_mono, 24)
        elif template_type == "Cyberverse Certificate":
            c.setFont(self.font_mono, 24)
        else:
            c.setFont(self.font_name, 24)
            
        c.drawCentredString(width / 2, height * 0.32, full_name)
        
        # 2. МІСЦЕ: білим кольором, центр сторінки
        # Для шаблону участі ця секція не виводиться
        if template_type != "Cyberverse Participation Certificate":
            place = get_field(["Місце", "Зайняте місце", "Rank", "Place"])
            if place:
                c.setFillColorRGB(1, 1, 1)
                c.setFont(self.font_name, 32)
                c.drawCentredString(width / 2.1, height * 0.23, str(place))
            
        self.last_cyber_y = 100

    def _draw_letter(self, c, width, height, data):
        # Header
        c.setFont(self.font_bold, 16)
        c.drawString(50, height - 60, "КНУ імені Тараса Шевченка")
        c.setFont(self.font_name, 10)
        c.drawString(50, height - 75, "Факультет інформаційних технологій")
        
        c.setFont(self.font_bold, 20)
        c.drawCentredString(width / 2, height - 150, "ОФІЦІЙНИЙ ЛИСТ")

        # Data
        y_pos = height - 220
        c.setFont(self.font_name, 12)
        for key, value in data.items():
            line = f"{key}: {value}"
            c.drawString(70, y_pos, line)
            y_pos -= 25
            
        # Closing
        y_pos -= 50
        c.drawString(70, y_pos, "З повагою,")
        y_pos -= 20
        c.setFont(self.font_bold, 12)
        c.drawString(70, y_pos, "Прищепа О.О.")

    def _draw_application(self, c, width, height, data):
        # Header (Now moved further left as requested)
        c.setFont(self.font_name, 10)
        header_x_start = 60 # Changed from width - 280 to move it to the left
        y_pos = height - 78 # Moved down by 1 cm (from 50 to 78)
        
        lines = [
            "До Приймальної комісії",
            "Київського національного університету",
            "імені Тараса Шевченка",
            "Факультету інформаційних технологій"
        ]
        for line in lines:
            c.drawString(header_x_start, y_pos, line)
            y_pos -= 15
        
        y_pos -= 10
        last_name = data.get("Прізвище", "________________")
        first_name = data.get("Ім'я", "________________")
        middle_name = data.get("По батькові", "________________")
        full_name = f"{last_name} {first_name} {middle_name}"
        
        c.drawString(header_x_start, y_pos, f"від {full_name}")
        y_pos -= 12
        c.setFont(self.font_name, 8)
        c.drawString(header_x_start, y_pos, "(прізвище, ім’я, по батькові повністю)")
        
        y_pos -= 15
        c.setFont(self.font_name, 10)
        c.drawString(header_x_start, y_pos, f"дата народження: {data.get('Дата народження', '__.__.____')}")
        y_pos -= 15
        c.drawString(header_x_start, y_pos, f"контактний телефон: {data.get('Контактний телефон', '________________')}")
        y_pos -= 15
        c.drawString(header_x_start, y_pos, f"електронна пошта: {data.get('Електронна пошта', '________________')}")

        # Title (Centered)
        y_pos -= 50
        c.setFont(self.font_bold, 16)
        c.drawCentredString(width / 2, y_pos, "ЗАЯВА")
        
        y_pos -= 40
        margin = 60 # Reduced margin to use more width
        line_width = width - (2 * margin)
        c.setFont(self.font_name, 12)
        
        # Main body
        text_body = [
            f"Я, {full_name},",
            f"серія паспорту: {data.get('Паспорт (серія/номер) або УНЗР', '________________')},",
            "",
            "прошу допустити мене до участі у конкурсному відборі та зарахувати на навчання до",
            "Київського національного університету імені Тараса Шевченка на факультет",
            "Інформаційних технологій,",
            "",
            f"на освітній рівень: {data.get('Освітній рівень', '________________')}",
            "         (бакалавр / магістр)",
            "",
            f"за спеціальністю: {data.get('Спеціальність', '________________')},",
            f"форма навчання: {data.get('Форма навчання', '________________')}",
            "         (денна / заочна / дистанційна)",
            "",
            "Надаю згоду на обробку моїх персональних даних відповідно до чинного",
            "законодавства України."
        ]
        
        for line in text_body:
            if "(бакалавр / магістр)" in line or "(денна / заочна / дистанційна)" in line:
                c.setFont(self.font_name, 10)
            else:
                c.setFont(self.font_name, 12)
            
            if line:
                c.drawString(margin, y_pos, line)
            y_pos -= 20 # Increased line spacing slightly for better readability

        # Footer area for signatures
        y_pos -= 50
        c.setFont(self.font_bold, 10)
        c.drawString(margin, y_pos, "Підпис абітурієнта:")
        c.line(margin + 105, y_pos - 2, margin + 250, y_pos - 2)
        
        # Stamp and Director Info (Shifted right as requested)
        stamp_x = margin + 176 # Moved right by 2 cm (from 120 to 176)
        c.drawString(stamp_x, y_pos - 40, "Печатка:")
        
        y_pos -= 85 # Adjust y_pos to fit "Печатка" and "Director"
        c.setFont(self.font_name, 10)
        c.drawString(stamp_x, y_pos, "Директор: Прищепа О.О.")
        
        # Store y_pos for stamp/sig placement
        self.last_app_y = y_pos 

    def _draw_contract(self, c, width, height, data):
        margin = 100 # Increased margin to make it narrower
        y_pos = height - 120 # Start lower
        
        # 1. ШАПКА
        c.setFont(self.font_bold, 14)
        c.drawCentredString(width / 2, y_pos, "ДОГОВІР")
        y_pos -= 20
        c.drawCentredString(width / 2, y_pos, "про надання платних освітніх послуг")
        y_pos -= 40 # Відступ після заголовку
        
        c.setFont(self.font_name, 11)
        c.drawString(margin, y_pos, f"№ {data.get('Номер договору', '_______')}")
        c.drawRightString(width - margin, y_pos, f"м. Київ, {data.get('Дата договору', '_______')}")
        
        # 2. СТОРОНИ ДОГОВОРУ
        y_pos -= 30
        c.setFont(self.font_bold, 12)
        c.drawString(margin, y_pos, "1. СТОРОНИ ДОГОВОРУ")
        y_pos -= 15
        c.setFont(self.font_name, 10)
        c.drawString(margin, y_pos, "Київський національний університет імені Тараса Шевченка та")
        y_pos -= 15
        last_name = data.get("Прізвище", "")
        first_name = data.get("Ім'я", "")
        middle_name = data.get("По батькові", "")
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        c.drawString(margin, y_pos, f"фізична особа {full_name}, разом — Сторони.")

        # 3. ПРЕДМЕТ ДОГОВОРУ
        y_pos -= 25
        c.setFont(self.font_bold, 12)
        c.drawString(margin, y_pos, "2. ПРЕДМЕТ ДОГОВОРУ")
        y_pos -= 15
        c.setFont(self.font_name, 10)
        c.drawString(margin, y_pos, "2.1. Виконавець бере на себе зобов'язання надати Замовнику освітню послугу:")
        y_pos -= 15
        c.drawString(margin + 15, y_pos, f"- Спеціальність: {data.get('Спеціальність', '_______')}")
        y_pos -= 12
        c.drawString(margin + 15, y_pos, f"- Освітній рівень: {data.get('Освітній рівень', '_______')}")
        y_pos -= 12
        c.drawString(margin + 15, y_pos, f"- Форма навчання: {data.get('Форма навчання', '_______')}")

        # 4. ВАРТІСТЬ ТА ПОРЯДОК ОПЛАТИ
        y_pos -= 25
        c.setFont(self.font_bold, 12)
        c.drawString(margin, y_pos, "3. ВАРТІСТЬ ТА ПОРЯДОК ОПЛАТИ")
        y_pos -= 15
        c.setFont(self.font_name, 10)
        
        from crypto_utils import CryptoManager
        raw_amount = data.get('Загальна вартість (грн)', '0.00')
        display_amount = CryptoManager.format_amount_pdf(raw_amount)
        
        c.drawString(margin, y_pos, f"3.1. Загальна вартість послуг становить: {display_amount}.")
        y_pos -= 15
        c.drawString(margin, y_pos, f"3.2. Оплата здійснюється: {data.get('Варіанти оплати', '_______')}.")

        # 5. ПРАВА ТА ОБОВʼЯЗКИ СТОРІН
        y_pos -= 25
        c.setFont(self.font_bold, 12)
        c.drawString(margin, y_pos, "4. ПРАВА ТА ОБОВʼЯЗКИ СТОРІН")
        y_pos -= 15
        c.setFont(self.font_name, 9)
        rights_text = [
            "4.1. Виконавець зобов'язаний забезпечити якісне надання освітніх послуг.",
            "4.2. Замовник зобов'язаний своєчасно вносити плату та дотримуватись правил закладу.",
            "4.3. Сторони несуть відповідальність згідно з чинним законодавством України."
        ]
        for line in rights_text:
            c.drawString(margin, y_pos, line)
            y_pos -= 12

        # 6. СТРОК ДІЇ ДОГОВОРУ
        y_pos -= 15
        c.setFont(self.font_bold, 12)
        c.drawString(margin, y_pos, "5. СТРОК ДІЇ ДОГОВОРУ")
        y_pos -= 15
        c.setFont(self.font_name, 10)
        c.drawString(margin, y_pos, "5.1. Договір набирає чинності з моменту підписання та діє до повного виконання.")

        # 7. РЕКВІЗИТИ ТА ПІДПИСИ СТОРІН
        y_pos -= 30
        c.setFont(self.font_bold, 12)
        c.drawString(margin, y_pos, "6. РЕКВІЗИТИ ТА ПІДПИСИ СТОРІН")
        
        y_pos -= 25
        c.setFont(self.font_bold, 10)
        c.drawString(margin, y_pos, "ЗАМОВНИК (Студент):")
        c.drawRightString(width - margin, y_pos, "ВИКОНАВЕЦЬ (КНУ):")
        
        y_pos -= 15
        c.setFont(self.font_name, 9)
        # Student info column
        student_y = y_pos
        c.drawString(margin, student_y, f"ПІБ: {full_name}")
        student_y -= 12
        c.drawString(margin, student_y, f"Тел: {data.get('Контактний телефон', '_______')}")
        student_y -= 12
        c.drawString(margin, student_y, f"Email: {data.get('Електронна пошта', '_______')}")
        student_y -= 12
        c.drawString(margin, student_y, f"Документ: {data.get('Паспорт (серія/номер) або УНЗР', '_______')}")
        
        # University info column
        uni_y = y_pos
        c.drawRightString(width - margin, uni_y, "КНУ імені Тараса Шевченка")
        uni_y -= 12
        c.drawRightString(width - margin, uni_y, "вул. Володимирська, 60, м. Київ")
        uni_y -= 12
        c.drawRightString(width - margin, uni_y, "Директор: Прищепа О.О.")

        y_pos = min(student_y, uni_y) - 45 # Increased margin
        self.last_contract_y = y_pos # Store for signature/stamp placement
        
        c.setFont(self.font_name, 8)
        c.drawString(margin, y_pos, "____________________")
        c.drawString(margin, y_pos - 10, "(підпис абітурієнта)")
        
        c.drawRightString(width - margin, y_pos, "Директор: Прищепа О.О.")

    def get_static_template_text(self, template_type: str) -> list:
        """
        Returns a list of static text lines that are present in the PDF template
        but are not captured by dynamic data fields. 
        Used to ensure canonical text consistency between generation and verification.
        """
        if template_type == "Certificate of Achievement":
            return [
                "СЕРТИФІКАТ",
                "ПРО УСПІШНЕ ЗАВЕРШЕННЯ КУРСУ",
                "Цей сертифікат свідчить про те, що",
                "Київський національний університет імені Тараса Шевченка",
                "Факультет інформаційних технологій",
                "(підпис директора)",
                "Директор:",
                "Прищепа Олександра Олександрівна",
                "Підпис клієнта:",
                "(підпис клієнта)",
                "Директор: Прищепа О.О.",
                "Підпис клієнта: Директор: Прищепа О.О.",
                "(підпис клієнта) (підпис директора)",
                "Організатор/Платформа:",
                "Обсяг:",
                "год. | Рівень:",
                "Студентський квиток №:",
                "Дата завершення:"
            ]
        elif template_type == "Application Form":
            return [
                "(бакалавр / магістр)",
                "(денна / заочна / дистанційна)",
                "Інформаційних технологій,",
                "Київського національного університету",
                "Київського національного університету імені Тараса Шевченка на факультет",
                "Надаю згоду на обробку моїх персональних даних відповідно до чинного",
                "Факультету інформаційних технологій",
                "законодавства України.",
                "прошу допустити мене до участі у конкурсному відборі та зарахувати на навчання до",
                "імені Тараса Шевченка",
                "До Приймальної комісії",
                "(прізвище, ім’я, по батькові повністю)",
                "Підпис абітурієнта:",
                "Печатка:",
                "Директор: Прищепа О.О.",
                "ЗАЯВА",
                "дата народження:",
                "контактний телефон:",
                "електронна пошта:",
                "серія паспорту:",
                "на освітній рівень:",
                "за спеціальністю:",
                "форма навчання:"
            ]
        elif template_type == "Official Letter":
            return [
                "КНУ імені Тараса Шевченка",
                "Факультет інформаційних технологій",
                "ОФІЦІЙНИЙ ЛИСТ",
                "З повагою,",
                "Прищепа О.О."
            ]
        elif "Cyberverse" in template_type:
            return [
                "CYBERVERSE CERTIFICATE",
                "CYBERVERSE PARTICIPATION CERTIFICATE",
                "EVENT: CYBERVERSE_ THE COST OF SILENCE",
                "ISSUER_1: Снитюк В.Є.",
                "ISSUER_2: Пархоменко І.І.",
                "ROLE_1: Декан факультету інформаційних технологій",
                "ROLE_2: Завідувач кафедри кібербезпеки та захисту інформації"
            ]
        elif template_type == "Contract for Education":
            return [
                "1. СТОРОНИ ДОГОВОРУ",
                "2. ПРЕДМЕТ ДОГОВОРУ",
                "2.1. Виконавець бере на себе зобов'язання надати Замовнику освітню послугу:",
                "3. ВАРТІСТЬ ТА ПОРЯДОК ОПЛАТИ",
                "4. ПРАВА ТА ОБОВʼЯЗКИ СТОРІН",
                "4.1. Виконавець зобов'язаний забезпечити якісне надання освітніх послуг.",
                "4.2. Замовник зобов'язаний своєчасно вносити плату та дотримуватись правил закладу.",
                "4.3. Сторони несуть відповідальність згідно з чинним законодавством України.",
                "5. СТРОК ДІЇ ДОГОВОРУ",
                "5.1. Договір набирає чинності з моменту підписання та діє до повного виконання.",
                "6. РЕКВІЗИТИ ТА ПІДПИСИ СТОРІН",
                "ЗАМОВНИК (Студент):",
                "ВИКОНАВЕЦЬ (КНУ):",
                "Київський національний університет імені Тараса Шевченка та",
                "фізична особа , разом — Сторони.",
                "КНУ імені Тараса Шевченка",
                "про надання платних освітніх послуг",
                "3.1. Загальна вартість послуг становить:",
                "3.2. Оплата здійснюється:",
                "ПІБ:",
                "Тел:",
                "Email:",
                "Документ:",
                "вул. Володимирська, 60, м. Київ",
                "Директор: Прищепа О.О.",
                "____________________",
                "(підпис абітурієнта)",
                "ЗАМОВНИК (Студент): ВИКОНАВЕЦЬ (КНУ):",
                "Спеціальність:",
                "Освітній рівень:",
                "Форма навчання:",
                "№", "м. Київ,",
                "ДОГОВІР",
                "____________________ Директор: Прищепа О.О."
            ]
        return []

    def extract_structured_data(self, pdf_path: str) -> tuple:
        """
        Витягує структуру даних з PDF для канонізатора.
        Повертає (template_type, data_dict, other_text_list).
        """
        doc = fitz.open(pdf_path)
        full_text = []
        template_type = "Unknown"
        
        for page in doc:
            words = page.get_text("words")
            if not words: continue
            words.sort(key=lambda w: (w[1], w[0]))
            
            lines = []
            current_line = [words[0][4]]
            last_y = words[0][1]
            for i in range(1, len(words)):
                w = words[i]
                if abs(w[1] - last_y) < 5:
                    current_line.append(w[4])
                else:
                    lines.append(" ".join(current_line))
                    current_line = [w[4]]
                    last_y = w[1]
            lines.append(" ".join(current_line))
            full_text.extend(lines)
        doc.close()

        data_fields = {}
        text_blob = "\n".join(full_text)
        
        # Визначення типу шаблону та збір даних
        if "ОФІЦІЙНИЙ ЛИСТ" in text_blob.upper() or "ЛИСТ" in text_blob.upper() or "OFFICIAL LETTER" in text_blob.upper():
            template_type = "Official Letter"
            import re
            m = re.search(r'Recipient:?\s*(.*)', text_blob)
            if m: data_fields["Recipient"] = m.group(1).strip()
            m = re.search(r'Subject:?\s*(.*)', text_blob)
            if m: data_fields["Subject"] = m.group(1).strip()
            m = re.search(r'Date:?\s*(.*)', text_blob)
            if m:
                # Try to extract only the date, ignoring "З повагою" or other text if they got glued
                val = m.group(1).split("З повагою")[0].strip()
                data_fields["Date"] = val
            
        elif "Cyberverse" in text_blob.upper() or "THE COST OF SILENCE" in text_blob.upper() or "CYBERVERSE" in text_blob.upper():
             if "PARTICIPATION" in text_blob.upper():
                 template_type = "Cyberverse Participation Certificate"
             else:
                 template_type = "Cyberverse Certificate"
                 
             import re
             lines = text_blob.split('\n')
             
             non_empty_lines = [l.strip() for l in lines if l.strip()]
             
             # ПІБ
             if non_empty_lines:
                 # ПІБ зазвичай в центрі, може бути першим або другим значущим рядком
                 name_candidate = non_empty_lines[0]
                 if "CYBERVERSE" in name_candidate.upper():
                     name_candidate = non_empty_lines[1] if len(non_empty_lines) > 1 else ""
                 
                 name = name_candidate.replace("ЗА", "").replace("МІСЦЕ", "").strip()
                 parts = name.split()
                 if len(parts) >= 2:
                     data_fields["Прізвище"] = parts[0]
                     data_fields["Ім'я"] = parts[1]
                     if len(parts) >= 3:
                         data_fields["По батькові"] = " ".join(parts[2:])
                 
                 # Шукаємо Місце (цифри або римські)
                 if template_type != "Cyberverse Participation Certificate":
                     for line in non_empty_lines:
                         # Шукаємо римські I-V або арабські цифри
                         m_place = re.search(r'\b(I|II|III|IV|V|\d+)\b', line)
                         if m_place and "CYBERVERSE" not in line.upper():
                             val = m_place.group(1)
                             data_fields["Зайняте місце"] = val
                             data_fields["Місце"] = val # Для сумісності
                             break
        elif "СЕРТИФІКАТ" in text_blob.upper():
                template_type = "Certificate of Achievement"
                import re
                m = re.search(r'\"([^\"]+)\"', text_blob)
                if m: data_fields["Назва курсу"] = m.group(1)
                m = re.search(r'Платформа:?\s*(.*)', text_blob)
                if m: data_fields["Платформа"] = m.group(1).split('\n')[0].strip()
                m = re.search(r'Обсяг:?\s*(\d+)', text_blob)
                if m: data_fields["Кількість годин"] = m.group(1)
                m = re.search(r'Рівень:?\s*([^|\n]+)', text_blob)
                if m: data_fields["Рівень курсу"] = m.group(1).strip()
                m = re.search(r'Студентський квиток №:?\s*(.*)', text_blob)
                if m: data_fields["Номер студентського"] = m.group(1).split('\n')[0].strip()
                m = re.search(r'Дата завершення:?\s*(.*)', text_blob)
                if m: data_fields["Дата завершення"] = m.group(1).split('\n')[0].strip()
                m = re.search(r'(?:свідчить про те, що|засвідчує, що)\n?([^\n]+)', text_blob, re.IGNORECASE)
                if m:
                    name = m.group(1).strip()
                    parts = name.split()
                    if len(parts) >= 3:
                        data_fields["Прізвище"] = parts[0]
                        data_fields["Ім'я"] = parts[1]
                        data_fields["По батькові"] = " ".join(parts[2:])

        elif "ЗАЯВА" in text_blob.upper():
            template_type = "Application Form"
            import re
            
            # Шукаємо всі ПІБ у документі
            # Пріоритет віддаємо ПІБ у тілі заяви (після "Я,"), 
            # бо саме воно зазвичай підробляється або є найбільш повним.
            m_ya = re.search(r'Я,\s+([^\n,(]+)', text_blob)
            m_vid = re.search(r'від\s+([^\n,(]+)', text_blob)
            
            name_to_use = None
            if m_ya:
                name_to_use = m_ya.group(1).strip()
            elif m_vid:
                name_to_use = m_vid.group(1).strip()
                
            if name_to_use:
                parts = name_to_use.split()
                if len(parts) >= 3:
                    data_fields["Прізвище"] = parts[0]
                    data_fields["Ім'я"] = parts[1]
                    data_fields["По батькові"] = " ".join(parts[2:])
            
            patterns = {
                "Дата народження": r"дата народження:?\s*([^\n,]+)",
                "Контактний телефон": r"контактний телефон:?\s*([^\n,]+)",
                "Електронна пошта": r"електронна пошта:?\s*([^\n,]+)",
                "Паспорт (серія/номер) або УНЗР": r"серія паспорту:?\s*([^\n,]+)",
                "Освітній рівень": r"на освітній рівень:?\s*([^\n]+)",
                "Спеціальність": r"за спеціальністю:?\s*([^\n,]+)",
                "Форма навчання": r"форма навчання:?\s*([^\n]+)"
            }
            for k, p in patterns.items():
                m = re.search(p, text_blob, re.IGNORECASE)
                if m: 
                    val = m.group(1).strip()
                    # Очистка від технічних приміток у дужках
                    val = re.split(r'\s*\(', val)[0].strip()
                    data_fields[k] = val

        elif "ДОГОВІР" in text_blob.upper():
            template_type = "Contract for Education"
            import re
            
            # Diagnostic print if needed
            # print(f"DEBUG: Text blob:\n{text_blob}")

            m = re.search(r'№\s*([^\s]+)\s+м\.\s+Київ,\s*([^\n]+)', text_blob)
            if m:
                data_fields["Номер договору"] = m.group(1).strip()
                data_fields["Дата договору"] = m.group(2).strip()
            
            m = re.search(r'фізична особа\s+([^\n,]+)', text_blob)
            if m:
                name = m.group(1).strip()
                parts = name.split()
                if len(parts) >= 3:
                    data_fields["Прізвище"] = parts[0]
                    data_fields["Ім'я"] = parts[1]
                    data_fields["По батькові"] = " ".join(parts[2:])
            
            # Use finditer and take the LAST match for specific fields (Price, Phone, Email, Document)
            # because they appear multiple times but the actual data is at the bottom (requisites).
            # Price appears in section 3.1 and then again? No, price is in 3.1.
            # Requisites have ПІБ, Тел, Email, Документ.
            
            patterns = {
                "Спеціальність": r"Спеціальність:?\s*([^\n]+)",
                "Освітній рівень": r"Освітній рівень:?\s*([^\n]+)",
                "Форма навчання": r"Форма навчання:?\s*([^\n]+)",
                "Загальна вартість (грн)": r"становить:?\s*([\d\s,]+)",
                "Варіанти оплати": r"Оплата здійснюється:?\s*([^\.]+)",
            }
            
            requisite_patterns = {
                "Контактний телефон": r"Тел:?\s*([^\n]+)",
                "Електронна пошта": r"Email:?\s*([^\n]+)",
                "Паспорт (серія/номер) або УНЗР": r"Документ:?\s*([^\n]+)"
            }

            # Check if there are multiple matches for crucial fields and ensure we don't pick the wrong one.
            # For Price, we should check if multiple distinct prices are present.
            price_matches = list(re.finditer(r"становить:?\s*([\d\s,]+)", text_blob, re.IGNORECASE))
            if len(price_matches) > 1:
                # If we have multiple prices, and they are DIFFERENT, this is a clear sign of tampering.
                # The first one might be the original (e.g. if it was hidden by white box but text is still there),
                # the second one might be the new one.
                prices = [m.group(1).replace(" ", "").replace(",", ".") for m in price_matches]
                if len(set(prices)) > 1:
                    # Mark that we found conflicting data
                    data_fields["_conflicting_data"] = True

            for k, p in patterns.items():
                matches = list(re.finditer(p, text_blob, re.IGNORECASE))
                if matches:
                    val = matches[-1].group(1).strip()
                    if k == "Загальна вартість (грн)":
                        val = val.replace("грн", "").strip()
                    data_fields[k] = val
            
            for k, p in requisite_patterns.items():
                # Take the LAST match for requisites
                matches = list(re.finditer(p, text_blob, re.IGNORECASE))
                if matches:
                    val = matches[-1].group(1).strip()
                    val = val.split("вул.")[0].split("Директор:")[0].split("КНУ")[0].strip()
                    data_fields[k] = val

        # Тепер збираємо "OTHER TEXT" - все, що не потрапило в data_fields і не є шаблоном
        other_text = []
        
        # Отримуємо повний список статичних фраз з шаблону
        static_lines = self.get_static_template_text(template_type)
        # Додаткові ключові слова, які зазвичай є частиною інтерфейсу/шаблону
        template_keywords = [
            "СЕРТИФІКАТ", "ЗАЯВА", "ДОГОВІР", "ПІБ", "Тел", "Email", "Документ", 
            "Підпис", "Печатка", "Директор", "Прищепа", "м. Київ", "КНУ", 
            "ЗАМОВНИК", "ВИКОНАВЕЦЬ", "підпис абітурієнта"
        ]
        
        # Для перевірки на дублювання значень полів (напр. підміна ціни)
        field_values_found = []
        for k, v in data_fields.items():
            if v and len(str(v)) > 2:
                field_values_found.append(str(v).upper())

        for line in full_text:
            line = line.strip()
            if not line or len(line) < 3: continue
            
            # 1. Перевіряємо на точний збіг зі статичними лініями шаблону
            is_static = False
            for sl in static_lines:
                if sl.upper() == line.upper() or line.upper() in sl.upper():
                    is_static = True
                    break
            if is_static: continue

            # 2. Перевіряємо, чи це значення якогось поля
            is_val = False
            
            # Спеціальна перевірка для рядків з даними:
            # Якщо лінія містить "Загальна вартість послуг становить: 10 000,00"
            # а в data_fields у нас "45 000,00", то ця лінія НЕ є відомою і має піти в other_text
            for k, v in data_fields.items():
                if not v or len(str(v)) < 3: continue
                val_str = str(v).upper()
                line_upper = line.upper()

                # Якщо лінія містить значення поля
                if val_str in line_upper:
                    # Спеціальна обробка для договору
                    if template_type == "Contract for Education":
                        # Перевіряємо, чи ця лінія є частиною секції, де очікується це поле
                        if k == "Загальна вартість (грн)" and "ВАРТІСТЬ" in line_upper:
                            # Перевірка: чи немає в цій лінії іншого числа, схожого на ціну?
                            # Якщо в лінії є інша сума, це TAMPERED.
                            # Для простоти поки просто вважаємо що це воно, але
                            # за замовчуванням TAMPERED знайдеться через ECDSA якщо ціна була основна.
                            # А якщо це просто текст поруч - ECDSA може не врятувати якщо extraction shadowing.
                            is_val = True
                            break
                        if k == "Спеціальність" and "СПЕЦІАЛЬНІСТЬ" in line_upper:
                            is_val = True
                            break
                        if k in ["Прізвище", "Ім'я", "По батькові"] and ("ФІЗИЧНА ОСОБА" in line_upper or "ПІБ:" in line_upper):
                            is_val = True
                            break
                        if k == "Контактний телефон" and "ТЕЛ:" in line_upper:
                            is_val = True
                            break
                        if k == "Електронна пошта" and "EMAIL:" in line_upper:
                            is_val = True
                            break
                        if k == "Паспорт (серія/номер) або УНЗР" and "ДОКУМЕНТ:" in line_upper:
                            is_val = True
                            break
                        if k in ["Освітній рівень", "Форма навчання", "Варіанти оплати", "Номер договору", "Дата договору"]:
                             is_val = True
                             break
                    else:
                        is_val = True
                        break

                # Якщо лінія ідентична значенню
                if line_upper == val_str:
                    is_val = True
                    break

            if is_val: continue
            
            # 3. Якщо лінія містить лише технічні заголовки (напр. "ПІБ:"), ігноруємо
            is_keyword = False
            for k in template_keywords:
                if k.upper() == line.upper(): # Тільки точний збіг для ключових слів в other_text
                    is_keyword = True
                    break
            if is_keyword: continue
            
            # 4. Ігноруємо якщо це частина назви університету або факультету (статичний текст)
            # Тільки якщо лінія ПОВНІСТЮ збігається з однією з відомих частин
            known_entities = [
                "Київський національний університет імені Тараса Шевченка",
                "Факультет інформаційних технологій",
                "Інформаційних технологій",
                "Київського національного університету імені Тараса Шевченка",
                "Київського національного університету",
                "імені Тараса Шевченка"
            ]
            is_entity = False
            for ent in known_entities:
                if line.upper() == ent.upper():
                    is_entity = True
                    break
            if is_entity: continue

            other_text.append(line)

        return template_type, data_fields, other_text

    def get_other_text_from_data(self, template_type: str, data: dict) -> list:
        """Повертає очікуваний 'other text' при генерації (зазвичай порожній для чистих даних)."""
        return []

    def get_other_text(self, pdf_path: str) -> list:
        """Повертає текст, який не є частиною відомих шаблонів (для детекції TAMPERED)."""
        doc = fitz.open(pdf_path)
        other_lines = []
        
        # Список відомих фраз, які ми ігноруємо
        known = [
            "СЕРТИФІКАТ", "ЗАЯВА", "ДОГОВІР", "УНІВЕРСИТЕТ", "ФАКУЛЬТЕТ", 
            "ШЕВЧЕНКА", "Прищепа", "Директор", "Підпис", "Печатка",
            "Платформа", "Обсяг", "Рівень", "квиток", "Дата", "курсу",
            "Я,", "від", "на народження", "телефон", "пошта", "паспорту",
            "рівень", "спеціальністю", "навчання", "№", "м. Київ",
            "фізична особа", "Сторони", "вартість", "Оплата", "Тел", "Email", "Документ"
        ]
        
        for page in doc:
            text = page.get_text()
            for line in text.split('\n'):
                line = line.strip()
                if not line or len(line) < 3: continue
                
                is_known = any(k.upper() in line.upper() for k in known)
                if not is_known:
                    # Перевіряємо, чи це не значення поля (ПІБ, назва курсу тощо)
                    # Якщо лінія дуже коротка або схожа на технічну — ігноруємо
                    other_lines.append(line)
        doc.close()
        return other_lines

    def render_pdf_page_to_pixels(self, pdf_path: str, page_index: int = 0, dpi: int = 200) -> bytes:
        """
        Deterministically renders a PDF page to a raster image and returns raw RGB pixel data.
        To ensure stability against steganographic changes, we ignore the background image layer.
        """
        doc = fitz.open(pdf_path)
        page = doc[page_index]
        
        # 1. Hide images (background) during rendering
        # We can do this by using a display list or by removing images temporarily
        # Easier way: get_pixmap has 'annots' and 'layers' but hiding images is tricky.
        # Alternative: use page.get_textbox or similar but we need pixels.
        
        # Let's try to remove all images from the page before rendering
        # This is destructive but we only do it on the 'page' object in memory
        for img in page.get_images():
            page.delete_image(img[0]) # img[0] is the xref
        
        # 200 DPI calculation (72 points per inch)
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        
        # Render to pixmap (RGB)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        
        pixel_data = pix.samples
        
        doc.close()
        return pixel_data

    def extract_background_image(self, pdf_path: str, seed: int) -> Image.Image:
        """
        Extracts the steganographic background image from the PDF.
        Tries to find an image that contains valid embedded data.
        """
        from steganography import SteganoManager
        doc = fitz.open(pdf_path)
        
        found_images = []
        for page in doc:
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                img = Image.open(io.BytesIO(base_image["image"]))
                
                # Check if this image has embedded data by looking at the first 4 bytes
                try:
                    data = SteganoManager.extract_data(img, seed)
                    if len(data) > 0:
                        doc.close()
                        return img
                except:
                    continue
                
                found_images.append(img)

        doc.close()
        if found_images:
            # Fallback to the largest image if no data found
            found_images.sort(key=lambda x: x.size[0] * x.size[1], reverse=True)
            return found_images[0]
            
        raise ValueError("No background image found in PDF.")
