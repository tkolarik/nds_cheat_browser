# utils/header_crc32.py

import binascii
import os

def calculate_jamcrc(file_path, header_size=512):
    """
    Calculates the JAMCRC (bitwise NOT of CRC-32) of the ROM header.

    Args:
        file_path (str): Path to the ROM file.
        header_size (int): Number of bytes to read from the header (default: 512).

    Returns:
        str: The JAMCRC as an 8-character hexadecimal string (e.g., '4DFFBF91') or None if calculation fails.
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(header_size)
            if not header:
                print(f"Error: File '{file_path}' is empty or cannot be read.")
                return None
            # Compute CRC32
            crc32 = binascii.crc32(header) & 0xFFFFFFFF
            # Compute JAMCRC by applying bitwise NOT
            jamcrc = (~crc32) & 0xFFFFFFFF
            # Format as uppercase hexadecimal without '0x', zero-padded to 8 characters
            return f"{jamcrc:08X}"
    except Exception as e:
        print(f"Error calculating JAMCRC for '{file_path}': {e}")
        return None
