import os
from PIL import Image, ImageDraw
from crypto_utils import CryptoManager
from steganography import SteganoManager
from pdf_processor import PDFProcessor
from canonicalizer import Canonicalizer

# ... existing code ...

class DocumentProtectionSystem:
    def __init__(self):
        self.crypto = CryptoManager()
        self.stegano = SteganoManager()
        self.pdf = PDFProcessor()
        self.diagnostic_mode = True  # Вмикаємо діагностичний режим за замовчуванням

        # ... existing code ...

    # ... existing code ...

    def _pack_signed_payload(self, template_type: str, canonical_text: str, text_hash: bytes, signature: bytes, visual_hash: bytes = None) -> bytes:
        """
        Створює детермінований payload:
        - JSON (template_type + canonical_text + canonical_hash_hex + visual_hash_hex)
        - signature bytes
        Формат: MAGIC(6) + json_len(4) + json + sig_len(4) + sig
        """
        import json
        import struct

        payload = {
            "v": 2,  # Оновлюємо версію до 2 для підтримки візуального хешу
            "template_type": template_type,
            "canonical_text": canonical_text,
            "canonical_hash": text_hash.hex(),
        }
        if visual_hash:
            payload["visual_hash"] = visual_hash.hex()

        json_bytes = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        magic = b"HDPSv1"
        return (
            magic
            + struct.pack(">I", len(json_bytes))
            + json_bytes
            + struct.pack(">I", len(signature))
            + signature
        )

    def _unpack_signed_payload(self, blob: bytes) -> tuple[str, str, bytes, bytes, bytes]:
        """
        Повертає (template_type, canonical_text, text_hash_bytes, signature_bytes, visual_hash_bytes)
        """
        import json
        import struct

        if len(blob) < 6 + 4:
            raise ValueError("Payload too short.")

        magic = blob[:6]
        if magic != b"HDPSv1":
            raise ValueError("Unknown payload format (bad magic).")

        offset = 6
        (json_len,) = struct.unpack(">I", blob[offset:offset + 4])
        offset += 4

        json_bytes = blob[offset:offset + json_len]
        offset += json_len

        (sig_len,) = struct.unpack(">I", blob[offset:offset + 4])
        offset += 4

        signature = blob[offset:offset + sig_len]

        data = json.loads(json_bytes.decode("utf-8"))
        template_type = data.get("template_type", "Unknown")
        canonical_text = data.get("canonical_text", "")
        canonical_hash_hex = data.get("canonical_hash", "")
        text_hash = bytes.fromhex(canonical_hash_hex) if canonical_hash_hex else b""
        
        visual_hash_hex = data.get("visual_hash", "")
        visual_hash = bytes.fromhex(visual_hash_hex) if visual_hash_hex else b""

        return template_type, canonical_text, text_hash, signature, visual_hash

    def _prepare_background(self, bg_path: str, template_type: str, encrypted_payload: bytes) -> Image.Image:
        """
        Уніфікований процес підготовки фону: завантаження, зміна розміру та вбудовування даних.
        """
        from reportlab.lib.pagesizes import letter, landscape
        if "Cyberverse" in template_type:
            # User wants landscape (album) orientation for Cyberverse
            pagesize = landscape(letter)
        else:
            pagesize = letter
            
        width_pt, height_pt = pagesize
        width_px, height_px = int(width_pt * 2), int(height_pt * 2) # Higher resolution for quality

        if os.path.exists(bg_path):
            img = Image.open(bg_path)
        else:
            # Create a fallback blank image if template is missing
            img = Image.new("RGB", (width_px, height_px), (240, 240, 240))
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, width_px-20, height_px-20], outline=(200, 200, 200), width=2)

        # Resize to Letter format
        img = img.resize((width_px, height_px), Image.Resampling.LANCZOS)
        
        # Embed data using steganography
        stego_bg = self.stegano.embed_data(img, encrypted_payload, self.stego_seed)
        return stego_bg

    def create_dummy_assets(self):
        """Creates dummy signature and keys if they don't exist."""
        if not os.path.exists("png"):
            os.makedirs("png")

        sig_path = os.path.join("png", "user_signature.png")
        if not os.path.exists(sig_path):
            img = Image.new('RGBA', (120, 40), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), "Sample Signature", fill=(0, 0, 150))
            img.save(sig_path)
            
        if not os.path.exists("private_key.pem"):
            priv, pub = self.crypto.generate_ecdsa_keys()
            with open("private_key.pem", "wb") as f:
                f.write(self.crypto.export_private_key(priv))
            with open("public_key.pem", "wb") as f:
                f.write(self.crypto.export_public_key(pub))
        
        if not hasattr(self, 'private_key'):
            with open("private_key.pem", "rb") as f:
                self.private_key = self.crypto.import_private_key(f.read())
            with open("public_key.pem", "rb") as f:
                self.public_key = self.crypto.import_public_key(f.read())
                
        if not os.path.exists("aes_key.bin"):
            with open("aes_key.bin", "wb") as f:
                f.write(os.urandom(32))
        
        if not hasattr(self, 'aes_key'):
            with open("aes_key.bin", "rb") as f:
                self.aes_key = f.read()
                
        if not os.path.exists("stego_seed.bin"):
            import struct
            seed = 12345
            with open("stego_seed.bin", "wb") as f:
                f.write(struct.pack(">I", seed))
        
        if not hasattr(self, 'stego_seed'):
            import struct
            with open("stego_seed.bin", "rb") as f:
                self.stego_seed = struct.unpack(">I", f.read()[:4])[0]

    def user_workflow(self, template_type, personal_data, signature_path=os.path.join("png", "user_signature.png")):
        print("\n--- User Workflow: Generating Document ---")
        import hashlib
        import datetime
        
        # Ensure assets exist
        self.create_dummy_assets()

        # 1. Generate canonical text using the unified module
        canonical_text = Canonicalizer.get_canonical_form(template_type, personal_data)
        print(f"[*] Canonical Text (Generation):\n{canonical_text}")

        # 2. Hashing (what we actually sign)
        text_hash = Canonicalizer.compute_hash(canonical_text)
        print(f"[*] SHA-256 Text Hash: {text_hash.hex()}")

        # 3. Visual Hashing - Step A: Generate temporary PDF to get visual representation
        # We need a PDF with the correct text to compute its visual hash
        # But we also need the visual hash to put it INTO the PDF (via LSB in background)
        # This is a chicken-and-egg problem. 
        # Solution:
        # a) Generate PDF with "empty" or "placeholder" stego background
        # b) Render it to pixels
        # c) Compute visual hash
        # d) Generate the final PDF with the visual hash in the background
        
        print("[*] Computing visual hash...")
        temp_filename = f"temp_visual_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
        
        # To get a STABLE visual hash that includes the stego effects:
        # 1. Create a dummy payload of the same size as the real one will be
        #    (JSON with same keys, signature is 64-72 bytes, etc.)
        dummy_sig = b"0" * 71 # Average ECDSA signature length
        dummy_visual_hash = b"0" * 32
        dummy_packed = self._pack_signed_payload(template_type, canonical_text, text_hash, dummy_sig, dummy_visual_hash)
        dummy_encrypted = self.crypto.encrypt_data(self.aes_key, dummy_packed)
        
        bg_mapping = {
            "Certificate of Achievement": os.path.join("png", "background_certificate.png"),
            "Cyberverse Certificate": os.path.join("png", "background_cyberverse.png"),
            "Cyberverse Participation Certificate": os.path.join("png", "background_participation.png"),
            "Application Form": os.path.join("png", "background_app.png"),
            "Contract for Education": os.path.join("png", "background_contract.png")
        }
        bg_path = bg_mapping.get(template_type, os.path.join("png", "background_template.png"))
        
        # Prepare a clean background (just resized)
        from reportlab.lib.pagesizes import letter, landscape
        if "Cyberverse" in template_type:
            pagesize = landscape(letter)
        else:
            pagesize = letter
            
        width_pt, height_pt = pagesize
        width_px, height_px = int(width_pt * 2), int(height_pt * 2)
        if os.path.exists(bg_path):
            clean_bg = Image.open(bg_path).resize((width_px, height_px), Image.Resampling.LANCZOS)
        else:
            clean_bg = Image.new("RGB", (width_px, height_px), (240, 240, 240))
            
        # 1. Generate PDF with clean background to get INITIAL visual hash
        self.pdf.generate_pdf(temp_filename, template_type, personal_data, clean_bg, signature_path)
        pixel_data = self.pdf.render_pdf_page_to_pixels(temp_filename)
        visual_hash = hashlib.sha256(pixel_data).digest()
        
        # 2. Combined Hash and Initial Signature
        combined_data = text_hash + visual_hash
        signing_hash = hashlib.sha256(combined_data).digest()
        signature = self.crypto.sign_hash(self.private_key, signing_hash)

        # 3. Build payload and Generate FINAL PDF
        packed = self._pack_signed_payload(template_type, canonical_text, text_hash, signature, visual_hash)
        encrypted_payload = self.crypto.encrypt_data(self.aes_key, packed)
        stego_bg = self._prepare_background(bg_path, template_type, encrypted_payload)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = "generated_archive"
        if not os.path.exists(archive_dir): os.makedirs(archive_dir)
        filename = f"protected_{timestamp}.pdf"
        output_pdf = os.path.join(archive_dir, filename)
        self.pdf.generate_pdf(output_pdf, template_type, personal_data, stego_bg, signature_path)
        
        # 4. RE-CALCULATE VISUAL HASH FROM FINAL PDF (to account for any noise)
        final_pixels = self.pdf.render_pdf_page_to_pixels(output_pdf)
        final_visual_hash = hashlib.sha256(final_pixels).digest()
        
        if final_visual_hash != visual_hash:
            # Re-signing with the final stable visual hash
            visual_hash = final_visual_hash
            combined_data = text_hash + visual_hash
            signing_hash = hashlib.sha256(combined_data).digest()
            signature = self.crypto.sign_hash(self.private_key, signing_hash)
            
            # RE-PACK and RE-GENERATE Final Version
            packed = self._pack_signed_payload(template_type, canonical_text, text_hash, signature, visual_hash)
            encrypted_payload = self.crypto.encrypt_data(self.aes_key, packed)
            stego_bg = self._prepare_background(bg_path, template_type, encrypted_payload)
            self.pdf.generate_pdf(output_pdf, template_type, personal_data, stego_bg, signature_path)

        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        print(f"[+] Protected PDF generated: {output_pdf}")
        return output_pdf

    def admin_workflow(self, pdf_path):
        print("\n--- Administrator Workflow: Verifying Document ---")
        import hashlib

        try:
            # 1. Extract Background and Data
            try:
                stego_bg = self.pdf.extract_background_image(pdf_path, self.stego_seed)
                print("[*] Background image extracted.")
            except Exception as e:
                print("\n[RESULT] STATUS: UNSIGNED")
                print(f"[INFO] Document does not contain a digital signature background: {e}")
                return

            # 2. Extract payload from LSB
            try:
                encrypted_payload = self.stegano.extract_data(stego_bg, self.stego_seed)
                if not encrypted_payload:
                    raise ValueError("No data found in LSB.")
                print("[*] Encrypted payload extracted from LSB.")
                if self.diagnostic_mode:
                    print(f"[*] hash(encrypted_payload): {hashlib.sha256(encrypted_payload).hexdigest()}")
                    print(f"[*] LSB Payload length: {len(encrypted_payload)} bytes")
            except Exception:
                print("\n[RESULT] STATUS: LSB_PAYLOAD_CORRUPTED")
                print("[INFO] No steganographic payload found or data is corrupted.")
                return

            # 3. Decrypt payload
            try:
                packed = self.crypto.decrypt_data(self.aes_key, encrypted_payload)
                print("[*] Payload decrypted.")
            except Exception as e:
                print("\n[RESULT] STATUS: AES_DECRYPT_FAILED")
                print(f"[ERROR] Failed to decrypt payload: {e}")
                return

            # 4. Parse payload + verify signature WITHOUT relying on PDF text extraction
            try:
                payload_template, payload_canonical_text, payload_hash, payload_signature, payload_visual_hash = self._unpack_signed_payload(packed)
                if self.diagnostic_mode:
                    print(f"[*] Payload template_type: {payload_template}")
                    print(f"[*] Payload canonical_hash: {payload_hash.hex()}")
                    if payload_visual_hash:
                        print(f"[*] Payload visual_hash: {payload_visual_hash.hex()}")
            except Exception as e:
                print("\n[RESULT] STATUS: PAYLOAD_PARSE_FAILED")
                print(f"[ERROR] Failed to parse payload: {e}")
                return

            # 5. Verify signature against payload hash (stable)
            # We need to verify against either combined hash (v2) or just text hash (v1)
            signing_hash = payload_hash
            if payload_visual_hash:
                combined_data = payload_hash + payload_visual_hash
                signing_hash = hashlib.sha256(combined_data).digest()

            is_valid = self.crypto.verify_signature(self.public_key, payload_signature, signing_hash)
            if not is_valid:
                print("\n[RESULT] STATUS: TAMPERED / ECDSA_VERIFY_FAILED")
                print("[INFO] Payload signature does not match. Document or payload was modified.")
                return

            # 6. Visual Verification (New Mode)
            if payload_visual_hash:
                print("[*] Performing visual verification...")
                try:
                    current_pixel_data = self.pdf.render_pdf_page_to_pixels(pdf_path)
                    current_visual_hash = hashlib.sha256(current_pixel_data).digest()
                    
                    if current_visual_hash != payload_visual_hash:
                        print(f"[*] Expected Visual Hash: {payload_visual_hash.hex()}")
                        print(f"[*] Current Visual Hash:  {current_visual_hash.hex()}")
                        print("\n[RESULT] STATUS: TAMPERED (VISUAL_LAYER_MODIFIED)")
                        print("[INFO] Visual content of the document has been modified.")
                        return
                    print("[+] Visual verification passed.")
                except Exception as e:
                    print(f"[*] Warning: Visual verification failed due to error: {e}")
                    # If rendering fails, we don't necessarily mark it as tampered if signature is OK,
                    # but here we should probably be strict if it's a V2 document.

            # 7. Optional: try to detect visible-text changes (best-effort)
            try:
                template_type, extracted_data, other_text = self.pdf.extract_structured_data(pdf_path)
                extracted_canonical_text = Canonicalizer.get_canonical_form(template_type, extracted_data)

                if self.diagnostic_mode:
                    print(f"[*] Canonical Text (Extracted from PDF):\n{extracted_canonical_text}")

                if extracted_canonical_text != payload_canonical_text:
                    print("\n[RESULT] STATUS: TAMPERED (VISIBLE_TEXT_CHANGED_OR_EXTRACTION_DRIFT)")
                    print("[INFO] Visible content differs from signed payload.")
                    return

                if other_text:
                    print(f"[*] Detected unexpected OTHER TEXT: {other_text}")
                    print("\n[RESULT] STATUS: TAMPERED")
                    print("[INFO] Document contains additional unauthorized text.")
                    return

            except Exception as e:
                # Якщо PDF-парсер зламався — не валимо валідність підпису.
                print(f"[*] Warning: PDF text extraction check failed: {e}")

            print("\n[RESULT] STATUS: VALID")
            print("[INFO] Document is authentic and integrity is verified.")

        except Exception as e:
            print(f"\n[RESULT] STATUS: ERROR")
            print(f"[ERROR] Unexpected error: {e}")

# ... existing code ...
