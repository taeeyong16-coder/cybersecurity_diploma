import os
import sys
from main import DocumentProtectionSystem
from PIL import Image, ImageDraw

def test_validation():
    ds = DocumentProtectionSystem()
    
    # 1. Test Valid Certificate
    print("\n--- Testing Valid Certificate ---")
    cert_data = {
        "Прізвище": "Тестовий",
        "Ім'я": "Студент",
        "По батькові": "Іванович",
        "Назва курсу": "Python Security",
        "Платформа": "Coursera",
        "Кількість годин": "40",
        "Рівень курсу": "Advanced",
        "Номер студентського": "ID123456",
        "Дата завершення": "20.01.2026"
    }
    cert_pdf = ds.user_workflow("Certificate of Achievement", cert_data)
    ds.admin_workflow(cert_pdf)

    # 2. Test Valid Application
    print("\n--- Testing Valid Application Form ---")
    app_data = {
        "Прізвище": "Петренко",
        "Ім'я": "Петро",
        "По батькові": "Петрович",
        "Дата народження": "01.01.2000",
        "Контактний телефон": "0501234567",
        "Електронна пошта": "petro@example.com",
        "Паспорт (серія/номер) або УНЗР": "123456789",
        "Освітній рівень": "Бакалавр",
        "Спеціальність": "Кібербезпека",
        "Форма навчання": "Денна"
    }
    app_pdf = ds.user_workflow("Application Form", app_data)
    ds.admin_workflow(app_pdf)

    # 3. Test Valid Contract
    print("\n--- Testing Valid Contract for Education ---")
    contract_data = {
        "Номер договору": "2024/001",
        "Дата договору": "20.01.2024",
        "Прізвище": "Сидоренко",
        "Ім'я": "Сидір",
        "По батькові": "Сидорович",
        "Спеціальність": "Інформаційні технології",
        "Освітній рівень": "Магістр",
        "Форма навчання": "Заочна",
        "Загальна вартість (грн)": "50000,00",
        "Варіанти оплати": "Поквартально",
        "Контактний телефон": "0631112233",
        "Електронна пошта": "sydor@example.com",
        "Паспорт (серія/номер) або УНЗР": "987654321"
    }
    contract_pdf = ds.user_workflow("Contract for Education", contract_data)
    ds.admin_workflow(contract_pdf)

    # 4. Test Tampered Contract
    print("\n--- Testing Tampered Contract ---")
    import fitz
    doc = fitz.open(contract_pdf)
    page = doc[0]
    page.insert_text((100, 100), "TAMPERED TEXT", fontsize=12, color=(1, 0, 0))
    tampered_contract_pdf = "generated_archive/tampered_contract.pdf"
    doc.save(tampered_contract_pdf)
    doc.close()
    ds.admin_workflow(tampered_contract_pdf)

    # 5. Test Unsigned Document
    print("\n--- Testing Unsigned Document ---")
    # Create a PDF without embedding anything in background
    unsigned_pdf = "generated_archive/unsigned_doc.pdf"
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    c = canvas.Canvas(unsigned_pdf, pagesize=letter)
    c.drawString(100, 700, "Цей документ не має цифрового підпису.")
    # Add a normal background image without stego
    bg_path = os.path.join("png", "background_template.png")
    if os.path.exists(bg_path):
        c.drawImage(bg_path, 0, 0, width=612, height=792)
    c.save()
    ds.admin_workflow(unsigned_pdf)

if __name__ == "__main__":
    test_validation()
