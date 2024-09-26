import os
import re


def find_image_signatures(data, signatures):
    """Find image signatures in binary data."""
    positions = []
    for signature in signatures:
        signature_bytes = bytes.fromhex(signature)
        for match in re.finditer(re.escape(signature_bytes), data):
            positions.append((match.start(), signature))
    return positions


def extract_images_from_disk_image(disk_image_path, output_directory, chunk_size=1024 * 1024):
    """Extract images from a disk image file in chunks."""
    # Define signatures for different image types
    signatures = {
        'JPEG': 'FFD8FF',
        'PNG': '89504E47',
        'GIF': '47494638'
    }

    image_positions = []
    buffer = bytearray()
    buffer_overlap = bytearray()  # Buffer for overlap between chunks
    last_pos = 0

    # Open the disk image file
    with open(disk_image_path, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break

            # Append new chunk to the buffer
            buffer.extend(chunk)
            buffer.extend(buffer_overlap)  # Include overlap from previous chunk

            # Process buffer to find signatures
            positions = find_image_signatures(buffer, signatures.values())
            for pos, sig in positions:
                if pos >= len(buffer):
                    continue
                image_positions.append((last_pos + pos, sig))

            # Handle buffer overlap
            buffer_overlap = buffer[-len(chunk):]
            buffer = buffer[:len(chunk)]  # Keep only the current chunk plus overlap

            # Update last position
            last_pos += len(chunk)

    # Extract and save images
    extracted_images = {}
    for pos, sig in image_positions:
        signature = bytes.fromhex(sig)
        image_data = None
        end_pos = -1
        if sig == 'FFD8FF':  # JPEG
            end_pos = buffer.find(b'\xFF\xD9', pos) + 2
            if end_pos > pos:
                image_data = buffer[pos:end_pos]
                ext = '.jpg'
        elif sig == '89504E47':  # PNG
            end_pos = buffer.find(b'\x49\x45\x4E\x44\xAE\x42\x60\x82', pos) + 8
            if end_pos > pos:
                image_data = buffer[pos:end_pos]
                ext = '.png'
        elif sig == '47494638':  # GIF
            end_pos = buffer.find(b'\x00\x3B', pos) + 2
            if end_pos > pos:
                image_data = buffer[pos:end_pos]
                ext = '.gif'
        else:
            continue

        if image_data:
            image_type = signatures.get(sig)
            filename = os.path.join(output_directory, f"image_{pos}{ext}")
            with open(filename, 'wb') as img_file:
                img_file.write(image_data)
            extracted_images[filename] = image_type

    return extracted_images


# Example usage
disk_image_path = r'C:\Users\Hiller\Desktop\Image Copy.001'
output_directory = r'C:\Users\Hiller\Desktop\output_images'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

extracted_images = extract_images_from_disk_image(disk_image_path, output_directory)

print(f"Extracted images: {extracted_images}")
