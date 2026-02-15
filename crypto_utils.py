import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoManager:
    """
    Handles cryptographic operations: Hashing (SHA-256), 
    Digital Signatures (ECDSA SECP256R1), and Encryption (AES-GCM).
    """
    
    @staticmethod
    def validate_amount_ua(amount: str) -> str:
        """
        Validates and canonicalizes Ukrainian monetary amount.
        Input:  '45 000,00' or '45000,00'
        Output: '45000.00'
        """
        import re
        # Видалити всі пробіли
        clean_amount = amount.replace(" ", "")
        
        # Перевірити формат через регулярний вираз: цифри, одна кома, рівно 2 цифри після коми
        # Формат: XXXXX,XX
        if not re.fullmatch(r"^\d+,\d{2}$", clean_amount):
            raise ValueError("Некоректний формат суми. Очікується 'XXXXX,XX' (наприклад, 45000,00)")
        
        # Замінити кому на крапку
        canonical = clean_amount.replace(",", ".")
        
        return canonical

    @staticmethod
    def validate_phone_ua(phone: str) -> str:
        """
        Validates and canonicalizes Ukrainian mobile phone number.
        Input:  0XXXXXXXXX
        Output: +380XXXXXXXXX
        """
        import re
        # Видалити всі нецифрові символи
        clean_phone = re.sub(r"\D", "", phone)
        
        # Перевірити, що залишилось рівно 10 цифр
        if len(clean_phone) != 10:
            raise ValueError("Номер телефону має містити рівно 10 цифр (наприклад, 0501234567)")
            
        # Перевірити, що номер починається з 0
        if not clean_phone.startswith("0"):
            raise ValueError("Номер телефону має починатися з '0'")
            
        # Повернути канонічний формат
        return f"+38{clean_phone}"

    @staticmethod
    def normalize_identity(data: dict) -> dict:
        """
        Normalizes personal data for hashing.
        """
        normalized = data.copy()
        
        # Канонізація суми, якщо вона є
        if "Загальна вартість (грн)" in normalized:
            try:
                normalized["Загальна вартість (грн)"] = CryptoManager.validate_amount_ua(normalized["Загальна вартість (грн)"])
            except ValueError:
                pass
                
        # Канонізація телефону, якщо він є
        phone_keys = ["Контактний телефон", "Тел"]
        for key in phone_keys:
            if key in normalized:
                try:
                    normalized[key] = CryptoManager.validate_phone_ua(normalized[key])
                except ValueError:
                    pass

        # Канонізація паспортних даних
        passport_keys = ["Паспорт (серія/номер) або УНЗР", "Номер ID"]
        from validators import validate_passport_ua
        for key in passport_keys:
            if key in normalized:
                try:
                    normalized[key] = validate_passport_ua(normalized[key])
                except ValueError:
                    pass
                    
        return normalized

    @staticmethod
    def format_amount_pdf(canonical_amount: str) -> str:
        """
        Formats canonical amount for PDF display.
        Input:  '45000.00'
        Output: '45 000,00 грн'
        """
        try:
            parts = canonical_amount.split('.')
            integer_part = parts[0]
            decimal_part = parts[1]
            
            # Додаємо розділювач тисяч (пробіл)
            formatted_int = ""
            for i, char in enumerate(reversed(integer_part)):
                if i > 0 and i % 3 == 0:
                    formatted_int = " " + formatted_int
                formatted_int = char + formatted_int
                
            return f"{formatted_int},{decimal_part} грн"
        except (IndexError, ValueError):
            return f"{canonical_amount} грн"

    @staticmethod
    def compute_hash(data: str) -> bytes:
        """Computes SHA-256 hash of the input string."""
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data.encode('utf-8'))
        return digest.finalize()

    @staticmethod
    def generate_ecdsa_keys():
        """Generates a new ECDSA key pair (SECP256R1)."""
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def sign_hash(private_key, data_hash: bytes) -> bytes:
        """Signs the provided hash using ECDSA."""
        signature = private_key.sign(
            data_hash,
            ec.ECDSA(hashes.SHA256())
        )
        return signature

    @staticmethod
    def verify_signature(public_key, signature: bytes, data_hash: bytes) -> bool:
        """Verifies the ECDSA signature against the provided hash."""
        try:
            public_key.verify(
                signature,
                data_hash,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False

    @staticmethod
    def encrypt_data(key: bytes, plaintext: bytes) -> bytes:
        """Encrypts data using AES-GCM. Returns nonce + ciphertext + tag."""
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    @staticmethod
    def decrypt_data(key: bytes, encrypted_data: bytes) -> bytes:
        """Decrypts data using AES-GCM."""
        if len(encrypted_data) < 12:
            raise ValueError("Зашифровані дані занадто короткі (відсутній Nonce або дані пошкоджені).")
        aesgcm = AESGCM(key)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        try:
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise ValueError(f"Помилка при дешифруванні: {str(e)}")

    @staticmethod
    def export_private_key(private_key, password: str = None) -> bytes:
        encryption_algorithm = serialization.BestAvailableEncryption(password.encode()) if password else serialization.NoEncryption()
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )

    @staticmethod
    def export_public_key(public_key) -> bytes:
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def import_private_key(pem_data: bytes, password: str = None):
        return serialization.load_pem_private_key(
            pem_data,
            password=password.encode() if password else None
        )

    @staticmethod
    def import_public_key(pem_data: bytes):
        return serialization.load_pem_public_key(pem_data)
