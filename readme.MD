
# NDS Cheat Browser

A modern web interface for browsing and searching Nintendo DS cheat codes. Upload your ROM file to find matching cheats, or search through the database by game name or cheat content. Supports both desktop and mobile browsers.

## Features

- Upload NDS ROMs to automatically find matching cheats
- Search games by name or GameID
- Search cheats within a specific game
- Copy cheat names and codes with one click
- Responsive design - works on both desktop and mobile devices
- Clean, modern interface using Bootstrap
- Local network access support

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

1. Start the Flask server:
```bash
python app.py
```

2. Access the application:
- Local: http://127.0.0.1:5050
- Network: http://your-local-ip:5050 (e.g., http://192.168.1.100:5050)

## Usage

1. Open the web interface in your browser
2. Upload an NDS ROM file using the file selector
3. The application will automatically find and display matching cheats
4. Use the search bars to filter:
   - Game Search: Filter games by name or GameID
   - Cheat Search: Search within the current game's cheats
5. Click on folder and cheat names to expand their contents
6. Use the copy buttons to copy cheat names or codes to your clipboard

## File Structure

- `/data`: Place your `cheats.xml` file here
- `/gui`: Contains the optional tkinter-based desktop interface
- `/static`: CSS, JavaScript, and other static assets
- `/templates`: HTML templates
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

3. **Application not accessible from other devices**:
   - Check your firewall settings
   - Make sure you're using the correct IP address
   - Verify that port 5050 is not blocked

## Contributing

Feel free to open issues or submit pull requests with improvements!

## License

None

## Acknowledgments

- Built with Flask and Bootstrap
- Uses ndstool for ROM parsing