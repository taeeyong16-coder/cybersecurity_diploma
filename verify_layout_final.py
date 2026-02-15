from main import DocumentProtectionSystem
import os

def test_fix():
    dps = DocumentProtectionSystem()
    
    # Створюємо фіктивні дані
    personal_data = {
        "Прізвище": "ОЛДЛД",
        "Ім'я": "ОТОЮОТОЛТ",
        "По батькові": "ОТИОТРЛОЖ",
        "Назва курсу": "Ethical Hacking (Cisco NetAcad)",
        "Платформа": "Cisco",
        "Кількість годин": "70",
        "Рівень курсу": "Advanced",
        "Номер студентського": "5646563",
        "Дата завершення": "15.01.2026"
    }
    
    # Запускаємо воркфлоу
    pdf_path = dps.user_workflow("Certificate of Achievement", personal_data)
    
    if os.path.exists(pdf_path):
        print(f"Certificate generated at: {pdf_path}")
        
        # Перевіряємо валідацію
        dps.admin_workflow(pdf_path)
    else:
        print("Failed to generate PDF")

if __name__ == "__main__":
    test_fix()
