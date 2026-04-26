import csv
import os
import sys
import glob
from main import DocumentProtectionSystem

def run_cli():
    system = DocumentProtectionSystem()
    # Переконуємось, що всі ключі та ресурси створені
    system.create_dummy_assets()
    
    while True:
        print("\n=== Система гібридного захисту документів (CLI) ===")
        print("1. Масова ГЕНЕРАЦІЯ документів (з CSV)")
        print("2. Масова ПЕРЕВІРКА документів (у папці)")
        print("0. Вихід")
        
        choice = input("\nВиберіть опцію: ")
        
        if choice == "1":
            batch_generation(system)
        elif choice == "2":
            batch_verification(system)
        elif choice == "0":
            print("Завершення роботи.")
            break
        else:
            print("Невірний вибір. Спробуйте ще раз.")

def batch_generation(system):
    print("\n--- Масова генерація документів ---")
    
    # 1. Вибір шаблону
    print("\nДоступні шаблони:")
    print("1. Cyberverse Certificate")
    print("2. Certificate of Achievement")
    print("3. Application Form")
    print("4. Contract for Education")
    print("5. Cyberverse Participation Certificate")
    
    template_choice = input("Виберіть номер шаблону [1]: ") or "1"
    template_map = {
        "1": "Cyberverse Certificate",
        "2": "Certificate of Achievement",
        "3": "Application Form",
        "4": "Contract for Education",
        "5": "Cyberverse Participation Certificate"
    }
    template_type = template_map.get(template_choice, "Cyberverse Certificate")
    
    # 2. Вибір файлу з даними
    default_csv = "cyberverse_test.csv" if template_type == "Cyberverse Certificate" else "participants.csv"
    csv_path = input(f"Введіть шлях до CSV-файлу [{default_csv}]: ") or default_csv
    
    if not os.path.exists(csv_path):
        print(f"[!] Помилка: Файл {csv_path} не знайдено.")
        return

    # 3. Масова генерація
    print(f"\n[*] Початок генерації для шаблону: {template_type}")

    import csv

    try:
        # Використовуємо utf-8-sig для автоматичної обробки BOM (Byte Order Mark), який додає Excel
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            # 1. Автоматичне визначення роздільника (Sniffer)
            sample = f.read(1024)
            f.seek(0)  # Обов'язково повертаємо курсор на початок після читання sample
            try:
                detected_delimiter = csv.Sniffer().sniff(sample, delimiters=',;').delimiter
            except csv.Error:
                detected_delimiter = ';'  # За замовчуванням, якщо файл замалий або Sniffer не впорався

            # Читаємо всі рядки з визначеним роздільником
            reader = csv.reader(f, delimiter=detected_delimiter)
            all_lines = list(reader)

            if not all_lines:
                print(f"[!] Помилка: Файл {csv_path} порожній.")
                return  # Або sys.exit() залежно від контексту функції

            # Очищуємо заголовки
            fieldnames = [name.strip() for name in all_lines[0]]

            rows = []
            for line in all_lines[1:]:
                if not line or not any(line): continue
                row = {}
                for i, val in enumerate(line):
                    if i < len(fieldnames):
                        row[fieldnames[i]] = val.strip()
                rows.append(row)

            print(f"[*] Знайдено полів: {', '.join(fieldnames)} (Роздільник: '{detected_delimiter}')")

            # 2. Виносимо функцію за межі циклу для оптимізації продуктивності
            def find_val(row_dict, aliases):
                norm_aliases = [a.lower().strip().replace("’", "'") for a in aliases]
                for k, v in row_dict.items():
                    if k.lower().strip().replace("’", "'") in norm_aliases:
                        return str(v).strip()
                return ""

            count = 0
            for row in rows:
                if "Cyberverse" in template_type:
                    # Використовуємо оптимізовану find_val
                    prizv = find_val(row, ['Прізвище', 'Surname', 'Last Name'])
                    imya = find_val(row, ['Ім’я', "Ім'я", 'Name', 'First Name'])
                    pobat = find_val(row, ['По батькові', 'Middle Name', 'Patronymic'])
                    
                    if template_type == "Cyberverse Participation Certificate":
                        place = "" # Ignore place for participation template
                    else:
                        place = find_val(row, ['Місце', 'Зайняте місце', 'Place', 'Rank'])

                    name = f"{prizv} {imya} {pobat}".strip()
                    if not name:
                        name = find_val(row, ["ПІБ", "Full Name", "Name"])

                    # Оновлюємо row для передачі в систему
                    row['Прізвище'] = prizv
                    row["Ім'я"] = imya
                    row['По батькові'] = pobat
                    row['Місце'] = place
                else:
                    # Для інших шаблонів теж зробимо базову нормалізацію імені
                    imya_other = row.get('Ім’я') or row.get("Ім'я") or ""
                    row["Ім'я"] = imya_other
                    name = f"{row.get('Прізвище', '')} {imya_other}".strip()

                # Перевірка на порожність імені для попередження
                if not name and template_type == "Cyberverse Certificate":
                    # Додав \n щоб попередження не затиралося наступним print(end="\r")
                    print(f"\n[{count + 1}] ⚠️ Попередження: Рядок порожній або ПІБ не знайдено: {row}")

                # Вивід прогресу
                print(f"[{count + 1}] Обробка: {name}...", end="\r")

                # Виклик основного воркфлоу захисту
                try:
                    output_file = system.user_workflow(template_type, row)
                    count += 1
                except Exception as e:
                    print(f"\n[!] Помилка при генерації для {name}: {e}")

            print(f"\n[+] Успішно згенеровано {count} документів.")
            print(f"[!] Файли збережено в папці: generated_archive")

    except Exception as e:
        print(f"\n[!] Помилка при читанні CSV: {e}")

def batch_verification(system):
    print("\n--- Масова перевірка документів ---")
    
    folder_path = input("Введіть шлях до папки з PDF [generated_archive]: ") or "generated_archive"
    
    if not os.path.isdir(folder_path):
        print(f"[!] Помилка: Папка {folder_path} не існує.")
        return
        
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    
    if not pdf_files:
        print(f"[!] У папці {folder_path} не знайдено PDF файлів.")
        return
        
    print(f"[*] Знайдено {len(pdf_files)} файлів для перевірки.\n")
    
    valid_count = 0
    tampered_count = 0
    error_count = 0
    
    # Тимчасово вимкнемо діагностичний вивід для чистоти консолі
    old_diag = system.diagnostic_mode
    system.diagnostic_mode = False
    
    from io import StringIO
    
    for i, pdf_path in enumerate(pdf_files):
        filename = os.path.basename(pdf_path)
        print(f"[{i+1}/{len(pdf_files)}] Перевірка {filename}...", end=" ")
        
        # Перехоплюємо stdout щоб витягнути результат
        import sys
        old_stdout = sys.stdout
        sys.stdout = result_io = StringIO()
        
        try:
            system.admin_workflow(pdf_path)
            sys.stdout = old_stdout
            result_output = result_io.getvalue()
            
            if "[RESULT] STATUS: VALID" in result_output:
                print("✅ VALID")
                valid_count += 1
            elif "TAMPERED" in result_output:
                print("❌ TAMPERED")
                tampered_count += 1
            elif "UNSIGNED" in result_output:
                print("⚠️ UNSIGNED")
                error_count += 1
            else:
                print("❓ UNKNOWN")
                error_count += 1
                
        except Exception as e:
            sys.stdout = old_stdout
            print(f"💥 ERROR: {e}")
            error_count += 1
            
    system.diagnostic_mode = old_diag
    
    print("\n--- Підсумок перевірки ---")
    print(f"Всього файлів: {len(pdf_files)}")
    print(f"Валідних:      {valid_count}")
    print(f"Пошкоджених:   {tampered_count}")
    print(f"Інші (помилки): {error_count}")

if __name__ == "__main__":
    run_cli()
