from PIL import Image
import io
import random

class SteganoManager:
    """
    Handles LSB (Least Significant Bit) steganography in PNG images.
    Uses Random Spacing to distribute bits across the entire image.
    """

    @staticmethod
    def embed_data(image_input, data: bytes, seed: int) -> Image.Image:
        """
        Embeds binary data into the LSB of a PNG image using random spacing.
        image_input can be a file path (str) or a PIL Image object.
        Data format: [4 bytes length] + [actual data]
        """
        if isinstance(image_input, str):
            img = Image.open(image_input).convert('RGBA')
        else:
            img = image_input.convert('RGBA')
            
        width, height = img.size
        pixels = list(img.getdata())
        
        # Prepend 4 bytes length to the data
        data_len = len(data)
        data_to_hide = data_len.to_bytes(4, byteorder='big') + data
        
        # Convert data to bit stream
        bits = []
        for byte in data_to_hide:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        
        total_bits = len(bits)
        available_slots = len(pixels) * 3 # 3 channels (R, G, B)
        
        if total_bits > available_slots:
            raise ValueError("Data too large to embed in this image.")
        
        # Shuffle all possible bit positions using the seed
        all_indices = list(range(available_slots))
        random.Random(seed).shuffle(all_indices)
        
        # Select the first 'total_bits' indices from the shuffled list
        indices = all_indices[:total_bits]
        
        # Create a mutable copy of pixels
        new_pixels = [list(p) for p in pixels]
        
        for i, bit_idx in enumerate(indices):
            pixel_idx = bit_idx // 3
            channel_idx = bit_idx % 3 # 0:R, 1:G, 2:B
            
            val = new_pixels[pixel_idx][channel_idx]
            new_pixels[pixel_idx][channel_idx] = (val & ~1) | bits[i]
            
        # Convert back to list of tuples
        final_pixels = [tuple(p) for p in new_pixels]
        img.putdata(final_pixels)
        return img

    @staticmethod
    def extract_data(image: Image.Image, seed: int) -> bytes:
        """
        Extracts binary data from the LSB of a PNG image using random spacing.
        """
        img = image
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA')
            
        pixels = list(img.getdata())
        available_slots = len(pixels) * 3
        
        # Shuffle all possible bit positions using the same seed
        all_indices = list(range(available_slots))
        random.Random(seed).shuffle(all_indices)
        
        # Extract first 32 bits to get length
        len_bits = []
        for i in range(32):
            bit_idx = all_indices[i]
            pixel_idx = bit_idx // 3
            channel_idx = bit_idx % 3
            len_bits.append(pixels[pixel_idx][channel_idx] & 1)
            
        # Convert length bits to int
        data_len_bytes = bytearray()
        for i in range(0, 32, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | len_bits[i+j]
            data_len_bytes.append(byte)
            
        data_len = int.from_bytes(data_len_bytes, byteorder='big')
        
        # Додано перевірку на адекватність довжини (наприклад, не більше 100КБ та не менше 12 байт для AES-GCM)
        if data_len < 12 or data_len > 100000 or (data_len + 4) * 8 > available_slots:
             raise ValueError("Вилучена довжина даних недійсна (дані відсутні або зображення пошкоджене).")

        # Extract actual data bits (including length header)
        total_bits = (data_len + 4) * 8
        data_bits = []
        for i in range(total_bits):
            bit_idx = all_indices[i]
            pixel_idx = bit_idx // 3
            channel_idx = bit_idx % 3
            data_bits.append(pixels[pixel_idx][channel_idx] & 1)
            
        # Convert bits to bytes
        extracted_bytes = bytearray()
        for i in range(0, len(data_bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | data_bits[i+j]
            extracted_bytes.append(byte)
            
        return bytes(extracted_bytes[4 : 4 + data_len])

    @staticmethod
    def image_to_bytes(img: Image.Image) -> bytes:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    @staticmethod
    def bytes_to_image(img_bytes: bytes) -> Image.Image:
        return Image.open(io.BytesIO(img_bytes))
