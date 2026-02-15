import hashlib
import re

class Canonicalizer:
    """
    Єдиний модуль для канонізації тексту документів.
    Забезпечує ідентичність тексту при генерації та верифікації.
    """
    
    @staticmethod
    def normalize_string(text: str) -> str:
        """Нормалізація пробілів, регістру та видалення зайвих символів."""
        if not text:
            return ""
        # Видалення невидимих символів та нормалізація пробілів
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def normalize_date(date_str: str) -> str:
        """Уніфікація форматів дат."""
        # Очікуємо ДД.ММ.РРРР
        match = re.search(r'(\d{1,2})[\.\-/](\d{1,2})[\.\-/](\d{4})', date_str)
        if match:
            d, m, y = match.groups()
            return f"{int(d):02d}.{int(m):02d}.{y}"
        return date_str

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Уніфікація номерів телефонів."""
        clean_phone = re.sub(r"\D", "", phone)
        if len(clean_phone) == 10 and clean_phone.startswith("0"):
            return f"+38{clean_phone}"
        if len(clean_phone) == 12 and clean_phone.startswith("380"):
            return f"+{clean_phone}"
        return phone

    @staticmethod
    def normalize_amount(amount: str) -> str:
        """Уніфікація грошових сум."""
        # Видаляємо пробіли та "грн"
        clean = amount.replace(" ", "").replace("грн", "").replace(".", ",").strip()
        match = re.search(r'(\d+),(\d{2})', clean)
        if match:
            return f"{match.group(1)}.{match.group(2)}"
        return amount

    @staticmethod
    def get_canonical_form(template_type: str, data: dict) -> str:
        """
        Створює канонічний текст на основі полів.
        Використовує фіксований порядок полів (сортування за ключами).
        """
        # Якщо дані передані як словник (старий формат)
        if isinstance(data, dict):
            lines = [template_type.upper()]
            
            # Нормалізація значень перед збіркою
            normalized_data = {}
            for k, v in data.items():
                norm_k = Canonicalizer.normalize_string(k)
                
                if "дата" in norm_k.lower():
                    norm_v = Canonicalizer.normalize_date(str(v))
                elif "телефон" in norm_k.lower() or "тел" in norm_k.lower():
                    norm_v = Canonicalizer.normalize_phone(str(v))
                elif "вартість" in norm_k.lower() or "сума" in norm_k.lower():
                    norm_v = Canonicalizer.normalize_amount(str(v))
                else:
                    norm_v = Canonicalizer.normalize_string(str(v))
                    
                normalized_data[norm_k] = norm_v

            # Фіксований порядок (алфавітний за ключами)
            for k in sorted(normalized_data.keys()):
                lines.append(f"{k}: {normalized_data[k]}")
                
            # Додавання статичних відповідальних осіб
            if template_type == "Certificate of Achievement":
                lines.append("ISSUER: Прищепа Олександра Олександрівна")
                lines.append("ROLE: Директор")
            elif "Application Form" in template_type:
                lines.append("INSTITUTION: Київський національний університет імені Тараса Шевченка")
                lines.append("DIRECTOR: Прищепа О.О.")
            elif "Official Letter" in template_type:
                lines.append("INSTITUTION: Київський національний університет імені Тараса Шевченка")
                lines.append("DIRECTOR: Прищепа О.О.")
            elif "Contract for Education" in template_type:
                lines.append("REPRESENTATIVE: Прищепа Олександра Олександрівна")

            return "\n".join(lines)
        
        # НОВИЙ СПРОЩЕНИЙ ФОРМАТ: якщо data це просто список рядків (raw text)
        elif isinstance(data, list):
            # Очищуємо кожен рядок та фільтруємо порожні
            cleaned_lines = []
            for line in data:
                norm = Canonicalizer.normalize_string(line)
                if norm:
                    cleaned_lines.append(norm)
            return "\n".join(cleaned_lines)
            
        return str(data)

    @staticmethod
    def compute_hash(text: str) -> bytes:
        """Обчислення SHA-256 від тексту."""
        return hashlib.sha256(text.encode('utf-8')).digest()
