
import os
import hashlib
from main import DocumentProtectionSystem
from pdf_processor import PDFProcessor

def get_file_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def diagnose_file(sys, path):
    print(f"\n--- Diagnosing: {path} ---")
    if not os.path.exists(path):
        print("File not found!")
        return

    print(f"File Size: {os.path.getsize(path)} bytes")
    print(f"File SHA-256: {get_file_hash(path)}")
    
    # 1. Background Extraction
    print("\n[1] Background Extraction:")
    try:
        stego_bg = sys.pdf.extract_background_image(path, sys.stego_seed)
        import io
        img_byte_arr = io.BytesIO()
        stego_bg.save(img_byte_arr, format='PNG')
        bg_hash = hashlib.sha256(img_byte_arr.getvalue()).hexdigest()
        print(f"Background extracted. Hash: {bg_hash}")
        
        # 2. LSB Extraction
        print("\n[2] LSB Extraction:")
        encrypted_sig = sys.stegano.extract_data(stego_bg, sys.stego_seed)
        if encrypted_sig:
            print(f"LSB Data extracted. Length: {len(encrypted_sig)} bytes")
            print(f"LSB Data Hash: {hashlib.sha256(encrypted_sig).hexdigest()}")
            
            # 3. Decryption
            try:
                signature = sys.crypto.decrypt_data(sys.aes_key, encrypted_sig)
                print("Signature decrypted successfully.")
            except Exception as e:
                print(f"Decryption FAILED: {e}")
        else:
            print("LSB Data Extraction FAILED (None returned).")
    except Exception as e:
        print(f"Background/LSB process FAILED: {e}")

    # 4. Text Extraction
    print("\n[3] Text Extraction:")
    try:
        template_type, extracted_data, other_text = sys.pdf.extract_structured_data(path)
        print(f"Template Type: {template_type}")
        print(f"Extracted Data: {extracted_data}")
        print(f"Other Text: {other_text}")
        
        from canonicalizer import Canonicalizer
        canonical_text = Canonicalizer.get_canonical_form(template_type, extracted_data)
        text_hash = Canonicalizer.compute_hash(canonical_text)
        print(f"Canonical Text Hash: {text_hash.hex()}")
    except Exception as e:
        print(f"Text Extraction FAILED: {e}")

if __name__ == "__main__":
    sys = DocumentProtectionSystem()
    # Disable diagnostic mode in main to avoid double printing
    sys.diagnostic_mode = False
    
    files = [
        r"generated_archive\protected_20260122_140729.pdf",
        r"generated_archive\protected_20260122_140729_app.luminpdf.com.pdf",
        r"generated_archive\protected_20260122_140729F.pdf"
    ]
    
    for f in files:
        diagnose_file(sys, f)
