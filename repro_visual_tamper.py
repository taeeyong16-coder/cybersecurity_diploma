
from main import DocumentProtectionSystem
import os
from PIL import Image, ImageDraw

def test_visual_verification():
    system = DocumentProtectionSystem()
    
    # Дані для документа
    data = {
        "ПІБ": "Тестовий Користувач",
        "Курс": "Кібербезпека",
        "Дата": "24.01.2026",
        "ID": "12345"
    }
    
    print("\n--- ГЕНЕРАЦІЯ ДОКУМЕНТА ---")
    pdf_path = system.user_workflow("Certificate of Achievement", data)
    
    print("\n--- ВЕРИФІКАЦІЯ ОРИГІНАЛУ ---")
    system.admin_workflow(pdf_path)
    
    # Створюємо підробку (модифікуємо візуальний шар)
    print("\n--- СТВОРЕННЯ ПІДРОБКИ (ВІЗУАЛЬНОЇ) ---")
    import fitz
    doc = fitz.open(pdf_path)
    page = doc[0]
    # Малюємо прямокутник поверх тексту
    page.draw_rect([100, 100, 200, 120], color=(1, 0, 0), fill=(1, 0, 0))
    tampered_pdf = pdf_path.replace(".pdf", "_tampered.pdf")
    doc.save(tampered_pdf)
    doc.close()
    
    print(f"[*] Підроблений документ збережено: {tampered_pdf}")
    
    print("\n--- ВЕРИФІКАЦІЯ ПІДРОБКИ ---")
    system.admin_workflow(tampered_pdf)

    # Очищення
    # os.remove(pdf_path)
    # os.remove(tampered_pdf)

if __name__ == "__main__":
    test_visual_verification()
