# app.py

import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from utils.generate_gameid import generate_gameid
from utils.cheat_utils import load_cheats, parse_cheats, search_games, search_cheats

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max upload size: 50MB

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load and parse cheats data on startup
cheat_data_xml = load_cheats('data/cheats.xml')  # Ensure the path is correct
cheat_data = parse_cheats(cheat_data_xml)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'rom' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['rom']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith('.nds'):
        return jsonify({'error': 'Invalid file format. Only .nds files are allowed.'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    gameid = generate_gameid(filepath)
    if not gameid:
        return jsonify({'error': 'Failed to generate GameID. Ensure ndstool is installed and the ROM is valid.'}), 500

    # Split GameID into Game Code and JAMCRC
    try:
        game_code, jamcrc = gameid.split(' ')
    except ValueError:
        return jsonify({'error': 'Invalid GameID format.'}), 500

    # Lookup cheats by Game Code
    if game_code in cheat_data:
        data = cheat_data[game_code]
        response = {
            'gameid': gameid,
            'game_name': data['name'],
            'folders': data['folders']
        }
        return jsonify(response), 200
    else:
        return jsonify({'error': 'No cheats found for this GameID.'}), 404

@app.route('/search_games', methods=['GET'])
def search_games_route():
    search_term = request.args.get('q', '')
    filtered_cheats = search_games(cheat_data, search_term)
    return jsonify(filtered_cheats)

@app.route('/search_cheats', methods=['GET'])
def search_cheats_route():
    game_id = request.args.get('game_id', '').upper()
    search_term = request.args.get('q', '')
    filtered_cheats = search_cheats(cheat_data, game_id, search_term)
    return jsonify(filtered_cheats)

if __name__ == "__main__":
    app.run(debug=True)
