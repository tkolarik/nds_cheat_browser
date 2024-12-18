# app.py

import os
import logging
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from utils.generate_gameid import generate_gameid
from utils.cheat_utils import load_cheats, parse_cheats, search_games, search_cheats

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024  # Increased to 512MB

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load and parse cheats data on startup
cheat_data_xml = load_cheats('data/cheats.xml')  # Ensure the path is correct
if cheat_data_xml:
    cheat_data = parse_cheats(cheat_data_xml)
    logger.info("Cheat data successfully loaded and parsed.")
else:
    cheat_data = {}
    logger.error("Failed to load cheat data.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    logger.info("Received upload request.")
    if 'rom' not in request.files:
        logger.warning("No file part in the request.")
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['rom']
    if file.filename == '':
        logger.warning("No file selected for uploading.")
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith('.nds'):
        logger.warning(f"Invalid file format attempted: {file.filename}")
        return jsonify({'error': 'Invalid file format. Only .nds files are allowed.'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    logger.info(f"File saved to {filepath}.")

    gameid = generate_gameid(filepath)
    if not gameid:
        logger.error("Failed to generate GameID.")
        return jsonify({'error': 'Failed to generate GameID. Ensure ndstool is installed and the ROM is valid.'}), 500

    logger.info(f"Generated GameID: {gameid}")

    # Lookup cheats by full GameID
    if gameid in cheat_data:
        data = cheat_data[gameid]
        response = {
            'gameid': gameid,
            'game_name': data['name'],
            'folders': data['folders']
        }
        logger.info(f"Cheats found for GameID: {gameid}")
        return jsonify(response), 200
    else:
        logger.info(f"No cheats found for GameID: {gameid}")
        return jsonify({'error': 'No cheats found for this GameID.', 'gameid': gameid}), 404

@app.route('/search_games', methods=['GET'])
def search_games_route():
    search_term = request.args.get('q', '')
    logger.info(f"Searching games with term: {search_term}")
    filtered_cheats = search_games(cheat_data, search_term)
    return jsonify(filtered_cheats)

@app.route('/search_cheats', methods=['GET'])
def search_cheats_route():
    game_id = request.args.get('game_id', '')
    search_term = request.args.get('q', '')
    logger.info(f"Searching cheats for GameID: {game_id} with term: {search_term}")
    filtered_cheats = search_cheats(cheat_data, game_id, search_term)
    return jsonify(filtered_cheats)

@app.errorhandler(413)
def handle_large_file(error):
    logger.warning("Uploaded file is too large.")
    return jsonify({'error': 'File size exceeds the maximum limit. Please upload a smaller file.'}), 413

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port=5050, debug=False)
