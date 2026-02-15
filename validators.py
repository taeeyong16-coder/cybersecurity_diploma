import re

def validate_passport_book(value: str) -> str:
    """
    Validates and canonicalizes Ukrainian old-style passport (booklet).
    Format: 2 uppercase letters (Cyrillic or Latin) + 6 digits.
    Example: АА123456
    """
    # Remove all whitespace
    clean_value = "".join(value.split()).upper()
    
    # Pattern: 2 uppercase letters + 6 digits
    # Covers Latin A-Z and Cyrillic А-Я (including І, Ї, Є)
    pattern = r"^[A-ZА-ЯІЇЄ]{2}\d{6}$"
    
    if not re.fullmatch(pattern, clean_value):
        raise ValueError("Некоректний формат паспорта-книжечки. Очікується 2 літери та 6 цифр (наприклад, АА123456)")
    
    return clean_value

def validate_id_card(value: str) -> str:
    """
    Validates and canonicalizes Ukrainian ID card.
    Format: 9 digits.
    Example: 012345678
    """
    # Remove all whitespace
    clean_value = "".join(value.split())
    
    # Pattern: 9 digits
    pattern = r"^\d{9}$"
    
    if not re.fullmatch(pattern, clean_value):
        raise ValueError("Некоректний формат ID-картки. Очікується 9 цифр (наприклад, 012345678)")
    
    return clean_value

def validate_unzr(value: str) -> str:
    """
    Validates and canonicalizes Ukrainian UNZR (Unique Record Number).
    Format: 13 digits (optionally with a dash after 8th digit).
    Example: 12345678-90123 or 1234567890123
    """
    # Remove all whitespace
    clean_value = "".join(value.split())
    
    # Pattern: 8 digits, optional dash, 5 digits
    pattern = r"^\d{8}-?\d{5}$"
    
    if not re.fullmatch(pattern, clean_value):
        raise ValueError("Некоректний формат УНЗР. Очікується 13 цифр, можливо з дефісом (наприклад, 12345678-90123)")
    
    # Canonical form is just 13 digits
    return clean_value.replace("-", "")

def validate_passport_ua(value: str) -> str:
    """
    Universal validator for Ukrainian identity documents (Passport book, ID card, UNZR).
    """
    # Try UNZR (13 digits / 8-5)
    try:
        if len(value.replace("-", "").strip()) == 13:
            return validate_unzr(value)
    except ValueError:
        pass
        
    # Try ID Card (9 digits)
    try:
        if len(value.strip()) == 9:
            return validate_id_card(value)
    except ValueError:
        pass
        
    # Try Passport Book (2 letters + 6 digits)
    try:
        return validate_passport_book(value)
    except ValueError:
        pass
        
    raise ValueError(
        "Некоректний формат документа. Очікується:\n"
        "- Паспорт-книжечка (2 літери, 6 цифр)\n"
        "- ID-картка (9 цифр)\n"
        "- УНЗР (13 цифр або 8-5)"
    )
