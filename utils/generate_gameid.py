# utils/generate_gameid.py

import subprocess
import os
import sys
import logging
from .header_crc32 import calculate_jamcrc

logger = logging.getLogger(__name__)

def extract_game_code(file_path):
    """
    Extracts the Game Code from the ROM using ndstools.
    
    Args:
        file_path (str): Path to the ROM file.
    
    Returns:
        str: The Game Code (e.g., 'IPKE') or None if extraction fails.
    """
    try:
        # Run the ndstools command
        logger.debug(f"Running ndstool on {file_path}")
        result = subprocess.run(
            ['ndstool', '-i', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        # Parse the output to find the Game Code line
        for line in result.stdout.splitlines():
            if 'Game code' in line:
                # Example line:
                # 0x0C	Game code                	IPKE (NTR-IPKE-USA)
                parts = line.split('\t')
                if len(parts) >= 3:
                    game_code_full = parts[2].strip()
                    # Extract the first 4 characters as Game Code
                    game_code = game_code_full[:4]
                    logger.debug(f"Extracted Game Code: {game_code}")
                    return game_code.upper()
        logger.error(f"Game code not found in ndstools output for '{file_path}'.")
        return None
    except FileNotFoundError:
        logger.error("'ndstool' command not found. Please ensure ndstools is installed and in your PATH.")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running ndstools on '{file_path}': {e.stderr}")
        return None

def generate_gameid(file_path):
    """
    Generates the GameID by extracting the Game Code and calculating the JAMCRC.
    
    Args:
        file_path (str): Path to the ROM file.
    
    Returns:
        str: The GameID in the format '<GameCode> <JAMCRC>' or None if any step fails.
    """
    game_code = extract_game_code(file_path)
    if not game_code:
        logger.error("Failed to extract Game Code.")
        return None
    jamcrc = calculate_jamcrc(file_path)
    if not jamcrc:
        logger.error("Failed to calculate JAMCRC.")
        return None
    gameid = f"{game_code} {jamcrc}"
    logger.debug(f"Generated GameID: {gameid}")
    return gameid
