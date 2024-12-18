# NDS Cheat Browser

A Nintendo DS cheat code browser with two interfaces:
- A modern web interface for browser-based access, including from mobile devices
- A traditional desktop GUI for local use

Both interfaces allow you to browse and search Nintendo DS cheat codes, with support for ROM file uploading to find matching cheats.

## Features

- Two interface options:
  - Web interface (Flask-based) with network access
  - Desktop GUI (tkinter-based) for local use
- Upload NDS ROMs to automatically find matching cheats
- Search games by name or GameID
- Search cheats within a specific game
- Copy cheat names and codes with one click
- Folder-based organization of cheats
- Clean, modern interface (web) or traditional GUI (desktop)

## Prerequisites

- Python 3.10 or higher
- ndstool (must be installed and accessible in your system PATH)
- Conda or Mamba package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nds-cheat-browser.git
cd nds-cheat-browser
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate nds_cheat_browser
```
Or if you prefer mamba:
```bash
mamba env create -f environment.yml
mamba activate nds_cheat_browser
```

3. Create a `data` directory and place your `cheats.xml` file inside:
```bash
mkdir data
# Copy your cheats.xml file into the data directory
```

## Running the Application

Choose your preferred interface:

### Web Interface
1. Start the Flask server:
```bash
python app.py
```

2. Access the application:
- Local: http://127.0.0.1:5050
- Network: http://your-local-ip:5050 (e.g., http://192.168.1.100:5050)

### Desktop GUI
1. Launch the tkinter interface:
```bash
python gui/cheat_browser.py
```

## Usage

### Web Interface
1. Open the web interface in your browser
2. Upload an NDS ROM file using the file selector
3. The application will automatically find and display matching cheats
4. Use the search bars to filter:
   - Game Search: Filter games by name or GameID
   - Cheat Search: Search within the current game's cheats
5. Click on folder and cheat names to expand their contents
6. Use the copy buttons to copy cheat names or codes to your clipboard

### Desktop GUI
1. Launch the application
2. Use the search bar at the top to filter games
3. Browse the tree view to explore games, folders, and cheats
4. Select a cheat to view its details:
   - Notes will appear in the notes text area
   - Codes will appear in the codes text area
5. Use the cheat search to find specific cheats within a selected game
6. Select text and use Ctrl+C (Cmd+C on Mac) to copy

## File Structure

- `/data`: Place your `cheats.xml` file here
- `/gui`: Contains the tkinter-based desktop interface
- `/static`: CSS, JavaScript, and other static assets (web interface)
- `/templates`: HTML templates (web interface)
- `/utils`: Utility functions for parsing cheats and generating GameIDs

## Troubleshooting

1. **ndstool not found error**:
   - Ensure ndstool is installed and in your system PATH
   - On Linux/macOS, you can check with: `which ndstool`
   - On Windows, try: `where ndstool`

2. **Cheats not loading**:
   - Verify that `cheats.xml` is in the `data` directory
   - Check that the file is properly formatted XML
   - Ensure the file permissions allow read access

3. **Web interface not accessible from other devices**:
   - Check your firewall settings
   - Make sure you're using the correct IP address
   - Verify that port 5050 is not blocked

4. **GUI interface issues**:
   - Ensure tkinter is properly installed in your Python environment
   - Try running with `python -m gui.cheat_browser` if you have path issues
   - On Linux, install `python3-tk` if needed

## Contributing

Feel free to open issues or submit pull requests with improvements!

## License

[Add your chosen license here]

## Acknowledgments

- Built with Flask and Bootstrap (web interface)
- Built with tkinter (desktop interface)
- Uses ndstool for ROM parsing