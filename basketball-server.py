from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS
import requests
import json
import threading
import time
import os

# Create Flask app with static file support
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Enable CORS for all routes

# Global variable to store the latest game data
current_game_data = {
    'clock': '55:55',
    'home_score': '555',
    'guest_score': '555',
    'home_timeouts': 'III',
    'guest_timeouts': 'III',
    'period': '5TH',
    'period_desc': 'FIFTH QUARTER',
    'home_possession': '.',
    'guest_possession': '.',
    'home_fouls': '5',
    'guest_fouls': '5',
    'shot_clock': '5',
    'timeout_clock': '55:55'
}

class BasketballDataFetcher:
    def __init__(self, url):
        self.url = url
        self.fields_mapping = {
            'Main_Clock_Time__mm_ss_ss_t__': 'clock',
            'Home_Team_Score': 'home_score',
            'Guest_Team_Score': 'guest_score',
            'Home_Time_Outs_Left___Total': 'home_timeouts',
            'Guest_Time_Outs_Left___Total': 'guest_timeouts',
            'Period_Text___1st_____OT______OT_2__': 'period',
            'Period_Description___End_of_1st____': 'period_desc',
            'Home_Possession_Indicator______or_____': 'home_possession',
            'Guest_Possession_Indicator______or_____': 'guest_possession',
            'Home_Team_Fouls': 'home_fouls',
            'Guest_Team_Fouls': 'guest_fouls',
            'Shot_Clock_Time__mm_ss____': 'shot_clock',
            'Time_Out_Time__mm_ss____': 'timeout_clock'
        }

    def extract_field_value(self, data, field_name):
        try:
            for column in data['table'][0]['range']['column']:
                if column['name'] == field_name:
                    for row in data['table'][0]['range']['row']:
                        if row['title'] == 'Value':
                            for field in row['field']:
                                if field['name'] == field_name:
                                    return field['value'].strip() if field['value'].strip() else ''
            return ''
        except (KeyError, IndexError):
            return ''

    def fetch_data(self):
        global current_game_data
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            data = response.json()

            # Update the current game data
            for field, mapped_name in self.fields_mapping.items():
                value = self.extract_field_value(data, field)
                current_game_data[mapped_name] = value

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")

def update_data_loop(fetcher):
    while True:
        fetcher.fetch_data()
        time.sleep(0.1)  # Poll every 100ms

@app.route('/data')
def get_data():
    return jsonify(current_game_data)

@app.route('/')
def serve_html():
    return send_file('basketball-frontend.html')

# Add route for serving static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

def main():
    # URL of the basketball data
    url = "http://192.168.10.166//player/dataset/tables/RTD%2FAS5-Basketball.json"

    # Create and start the data fetcher thread
    fetcher = BasketballDataFetcher(url)
    fetch_thread = threading.Thread(target=update_data_loop, args=(fetcher,), daemon=True)
    fetch_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()