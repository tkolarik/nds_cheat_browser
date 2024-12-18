# utils/cheat_utils.py

import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

def load_cheats(filepath):
    """Loads cheat data from an XML file."""
    try:
        logger.debug(f"Loading cheats from {filepath}")
        tree = ET.parse(filepath)
        root = tree.getroot()
        return root
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except ET.ParseError:
        logger.error(f"Invalid XML format in {filepath}")
        return None

def get_text(element, tag):
    """
    Safely retrieves and strips text from a given tag within an XML element.

    Args:
        element (xml.etree.ElementTree.Element): The parent XML element.
        tag (str): The tag name to search for.

    Returns:
        str: The stripped text if available; otherwise, an empty string.
    """
    sub = element.find(tag)
    if sub is not None and sub.text:
        return sub.text.strip()
    return ""

def parse_cheats(root):
    """
    Parses the XML root and organizes cheats by game.

    Args:
        root (xml.etree.ElementTree.Element): The root of the XML tree.

    Returns:
        dict: A dictionary with GameIDs as keys and their corresponding cheats.
    """
    if root is None:
        logger.warning("No root provided for parsing cheats.")
        return {}

    cheats_data = {}
    for game in root.findall('game'):
        game_name = get_text(game, 'name')
        game_id = get_text(game, 'gameid')  # Retain spaces in GameID
        logger.debug(f"Parsing cheats for Game: {game_name} (ID: {game_id})")
        folders_info = []

        # Handle cheats directly under <game> without <folder>
        direct_cheats = game.findall('cheat')
        if direct_cheats:
            logger.debug(f"Found {len(direct_cheats)} direct cheats for game {game_id}")
            folders_info.append({
                'folder_name': 'General',
                'cheats': [
                    {
                        'name': get_text(cheat, 'name'),
                        'notes': get_text(cheat, 'note'),
                        'codes': get_text(cheat, 'codes')
                    }
                    for cheat in direct_cheats
                ]
            })

        # Handle cheats within <folder>
        for folder in game.findall('folder'):
            folder_name = get_text(folder, 'name')
            cheats_info = []
            for cheat in folder.findall('cheat'):
                cheat_name = get_text(cheat, 'name')
                cheat_notes = get_text(cheat, 'note')
                cheat_codes = get_text(cheat, 'codes')
                cheats_info.append({
                    'name': cheat_name,
                    'notes': cheat_notes,
                    'codes': cheat_codes
                })
            logger.debug(f"Found {len(cheats_info)} cheats in folder '{folder_name}' for game {game_id}")
            folders_info.append({
                'folder_name': folder_name,
                'cheats': cheats_info
            })

        cheats_data[game_id] = {
            'name': game_name,
            'folders': folders_info
        }

    logger.info(f"Parsed cheats for {len(cheats_data)} games.")
    return cheats_data

def search_games(cheats_data, search_term):
    """
    Searches for games by name or GameID.

    Args:
        cheats_data (dict): The parsed cheats data.
        search_term (str): The term to search for.

    Returns:
        dict: A filtered dictionary of cheats data matching the search term.
    """
    if not search_term:
        logger.debug("Empty search term provided for game search.")
        return cheats_data

    search_term = search_term.lower()
    filtered_data = {}
    for game_id, game_info in cheats_data.items():
        if search_term in game_info['name'].lower() or search_term in game_id.lower():
            filtered_data[game_id] = game_info
            logger.debug(f"Game matched: {game_info['name']} ({game_id})")
    logger.info(f"Found {len(filtered_data)} games matching the search term '{search_term}'.")
    return filtered_data

def search_cheats(cheats_data, game_id, search_term):
    """
    Searches for cheats within a specific game by cheat name, notes, or codes.

    Args:
        cheats_data (dict): The parsed cheats data.
        game_id (str): The GameID to search within.
        search_term (str): The term to search for.

    Returns:
        dict: The cheats data for the specified game, filtered by the search term.
    """
    if not game_id:
        logger.warning("No GameID provided for cheat search.")
        return {}

    if not search_term:
        logger.debug("Empty search term provided for cheat search.")
        return cheats_data.get(game_id, {})

    search_term = search_term.lower()
    game_info = cheats_data.get(game_id, {})
    if not game_info:
        logger.warning(f"GameID {game_id} not found in cheat data.")
        return {}

    filtered_folders = []
    for folder in game_info.get('folders', []):
        filtered_cheats = []
        for cheat in folder.get('cheats', []):
            if (search_term in cheat['name'].lower() or
                search_term in cheat['notes'].lower() or
                search_term in cheat['codes'].lower()):
                filtered_cheats.append(cheat)
        if filtered_cheats:
            filtered_folders.append({
                'folder_name': folder['folder_name'],
                'cheats': filtered_cheats
            })
            logger.debug(f"Folder '{folder['folder_name']}' has {len(filtered_cheats)} matching cheats.")

    logger.info(f"Found {len(filtered_folders)} folders with matching cheats for GameID {game_id}.")
    return {
        'name': game_info['name'],
        'folders': filtered_folders
    }
