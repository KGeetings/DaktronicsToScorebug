from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS
import requests
import json
import threading
import time
import os
import logging
import socket
import struct
import keyboard

# Set the logging level to ERROR
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Create Flask app with static file support
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Enable CORS for all routes

# statsData = r"data.json"
statsData = r"X:\\data.json"
# statsData = r"W:\\PC vs Montezuma Girls.json"

# Second Flask app for heatmap hosting
heatmap_app = Flask("heatmap_app", static_url_path="", static_folder=".")
CORS(heatmap_app)

# Global variables to store the game data
current_game_data = {}
current_sport = 'basketball'  # Default sport

# Global pause
paused = False
paused_lock = threading.Lock()
last_toggle_time = 0.0
TOGGLE_DEBOUNCE_SECONDS = 0.2

# Sport-specific configurations
SPORT_CONFIGS = {
	'basketball': {
		'data_template': {
			'sport': 'basketball',
			'clock': '55:55',
			'home_score': '123',
			'guest_score': '123',
			'home_timeouts': '3',
			'guest_timeouts': '2',
			'period': '5TH',
			'period_desc': '5TH Quarter',
			'home_possession': '.',
			'guest_possession': '.',
			'home_fouls': '5',
			'guest_fouls': '5',
			'shot_clock': '5',
			'timeout_clock': '00:00',
			'shot_clock_status': '1',
			'home_stats': '',
			'guest_stats': '',
			'home_stats_duration': 0,
			'guest_stats_duration': 0,
			'home_new_animation': True,
			'guest_new_animation': True,
		},
		'fields_mapping': {
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
			'Time_Out_Time__mm_ss____': 'timeout_clock',
			'Shot_Clock__0______or__z__': 'shot_clock_status',
		}
	},
	'volleyball': {
		'data_template': {
			'sport': 'volleyball',
			'clock': '00:00',
			'home_score': '10',
			'guest_score': '5',
			'home_timeouts': '2',
			'guest_timeouts': '1',
			'period': '1',
			'period_desc': '1st Set',
			'serving_team': '',
			'home_sets_won': '3',
			'guest_sets_won': '1',
			'timeout_clock': '',
			'home_stats': '',
			'guest_stats': '',
			'home_stats_duration': 0,
			'guest_stats_duration': 0,
			'home_new_animation': True,
			'guest_new_animation': True,
		},
		'fields_mapping': {
			'Main_Clock_Time__mm_ss_ss_t__': 'clock',
			'Home_Team_Score': 'home_score',
			'Guest_Team_Score': 'guest_score',
			'Home_Time_Outs_Left___Total': 'home_timeouts',
			'Guest_Time_Outs_Left___Total': 'guest_timeouts',
			'Game': 'set_number',
			'Game_Description___End_of_1st____': 'period_desc',
			'Serving_Team': 'serving_team',
			'Home_Games_Won': 'home_sets_won',
			'Guest_Games_Won': 'guest_sets_won',
			'Time_Out_Time__mm_ss____': 'timeout_clock',
		}
	},
	'football': {
		'data_template': {
			'sport': 'football',
			'clock': '15:00',
			'home_score': '0',
			'guest_score': '0',
			'home_timeouts': 'III',
			'guest_timeouts': 'III',
			'quarter': '1',
			'period_desc': '1st Quarter',
			'down': '1',
			'distance': '10',
			'yard_line': '50',
			'home_possession': '.',
			'guest_possession': '.',
			'play_clock': '40',
			'timeout_clock': '00:00',
			'home_stats': '',
			'guest_stats': '',
			'home_stats_duration': 0,
			'guest_stats_duration': 0,
			'home_new_animation': True,
			'guest_new_animation': True,
		},
		'fields_mapping': {
			'clock': 'clock',
			'home_score': 'home_score',
			'guest_score': 'guest_score',
			'home_timeouts': 'home_timeouts',
			'guest_timeouts': 'guest_timeouts',
			'quarter': 'quarter',
			'period_desc': 'period_desc',
			'down': 'down',
			'distance': 'distance',
			'yard_line': 'yard_line',
			'home_possession': 'home_possession',
			'guest_possession': 'guest_possession',
			'play_clock': 'play_clock',
			'timeout_clock': 'timeout_clock',
		}
	}
}

class StatsServer:
	"""
	The stats message format should be JSON:
		{
			"command": "stats",
			"team": "home",  // or "guest"
			"text": "<html formatted stats>",
			"duration": 10  // seconds (0 for infinite)
			"new_animation": true  // Triggers a new animation, or just updates text, default is True
		}
	To clear all stats:
		{
			"command": "clear_all"
		}
	Program will need to implement the following:
		Connects to the socket server (port 5001)
		Sends messages with a 4-byte length prefix (network byte order)
		Formats the JSON messages as shown above
		Examples of HTML formatted message:
			guest_stats = f'<div style="color:rgb(255, 215, 0);"><b>And One</b></div>#2 - Jacob Harman<br>Fouls: {home_fouls}&emsp;&emsp;Points: {home_score}<hr style="border-color:white;width:1500px;"<br>Shot 1 - Made<br>Shot 2 - Made'
			home_stats = f'<div style="color:rgb(255, 215, 0);"><b>Three Points</b></div>#1 - Kenyon Geetings<br>Fouls: {home_fouls}&emsp;&emsp;Points: {home_score}'
			home_stats = f'<div style="color:rgb(255, 215, 0);"><b>Fouled By</b></div>#1 - Kenyon Geetings<br>Fouls: {home_fouls}&emsp;&emsp;Points: {home_score}'
	"""
	def __init__(self, host='0.0.0.0', port=5001):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))
		self.sock.listen(1)
		self.clients = []

	def handle_client(self, client_socket):
		while True:
			try:
				# First receive the message length (4 bytes, network byte order)
				msg_len_bytes = client_socket.recv(4)
				if not msg_len_bytes:
					break

				msg_len = struct.unpack('!I', msg_len_bytes)[0]

				# Then receive the actual message
				message = b''
				while len(message) < msg_len:
					chunk = client_socket.recv(min(msg_len - len(message), 4096))
					if not chunk:
						break
					message += chunk

				if message:
					self.process_message(message.decode('utf-8'))

			except (socket.error, struct.error) as e:
				print(f"Socket error: {e}")
				break

		if client_socket in self.clients:
			self.clients.remove(client_socket)
		client_socket.close()

	def process_message(self, message):
		try:
			data = json.loads(message)
			if data.get('command') == 'clear_all':
				current_game_data['home_stats'] = ''
				current_game_data['guest_stats'] = ''
				current_game_data['home_stats_duration'] = 0
				current_game_data['guest_stats_duration'] = 0
				current_game_data['home_new_animation'] = True
				current_game_data['guest_new_animation'] = True
			elif data.get('command') == 'stats':
				team = data.get('team', '').lower()
				if team in ['home', 'guest']:
					current_game_data[f'{team}_stats'] = data.get('text', '')
					current_game_data[f'{team}_stats_duration'] = data.get('duration', 0)
					new_animation = data.get('new_animation', True)
					current_game_data[f'{team}_new_animation'] = new_animation

					# If duration is not 0 (infinite), start a timer to clear the stats
					if data.get('duration', 0) > 0:
						def clear_stats():
							time.sleep(data['duration'])
							current_game_data[f'{team}_stats'] = ''
							current_game_data[f'{team}_stats_duration'] = 0
							current_game_data[f'{team}_new_animation'] = new_animation

						threading.Thread(target=clear_stats, daemon=True).start()

		except json.JSONDecodeError as e:
			print(f"Error decoding message: {e}")

	def start(self):
		while True:
			client_socket, _ = self.sock.accept()
			self.clients.append(client_socket)
			client_thread = threading.Thread(
				target=self.handle_client,
				args=(client_socket,),
				daemon=True
			)
			client_thread.start()

class SportDataFetcher:
	def __init__(self, url, sport):
		self.url = url
		self.sport = sport.lower()
		if self.sport not in SPORT_CONFIGS:
			raise ValueError(f"Unsupported sport: {sport}. Supported sports: {list(SPORT_CONFIGS.keys())}")

		self.fields_mapping = SPORT_CONFIGS[self.sport]['fields_mapping']

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
		# If paused, skip fetching (sleep briefly to avoid tight loop)
		if is_paused():
			time.sleep(0.25)
			continue

		fetcher.fetch_data()
		time.sleep(0.250)  # Poll every 250ms

def is_paused():
	with paused_lock:
		return paused

def set_paused(value: bool):
    global paused
    with paused_lock:
        paused = bool(value)
    status = "PAUSED" if paused else "RESUMED"
    print(f"[Hotkey 'ctrl+alt+P'] Data updates {status}")

def toggle_paused():
	global last_toggle_time
	now = time.time()
	if now - last_toggle_time < TOGGLE_DEBOUNCE_SECONDS:
		return
	last_toggle_time = now
	set_paused(not is_paused())

def register_hotkeys():
    # single hotkey that toggles pause/resume when pressing 'P'
    keyboard.add_hotkey("ctrl+alt+p", toggle_paused)
    print("'ctrl+alt+P' (toggle pause/resume)")

@app.route('/data')
def get_data():
	return jsonify(current_game_data)

@app.route("/sportsData")
def get_sports_data():
	#data_path = r"X:\data.json"
	data_path = statsData

	if not os.path.exists(data_path):
		return jsonify({"error": "data.json not found"}), 404

	with open(data_path, "r") as f:
		data = json.load(f)

	return jsonify(data)

@app.route('/')
def serve_html():
	# Serve sport-specific HTML file if it exists
	sport_html = f"{current_sport}-frontend.html"
	if os.path.exists(sport_html):
		return send_file(sport_html)
	else:
		return send_file("basketball-frontend.html")  # Basketball fallback

# Add route for serving static files
@app.route('/<path:filename>')
def serve_static(filename):
	return send_from_directory('.', filename)

@heatmap_app.route("/")
def serve_heatmap():
	return send_file("heatmap.html")

@heatmap_app.route("/<path:filename>")
def serve_heatmap_static(filename):
	return send_from_directory(".", filename)

def run_heatmap_server():
	print("Heatmap server running on http://localhost:5002")
	heatmap_app.run(host="0.0.0.0", port=5002)

def initialize_sport_data(sport):
	"""Initialize the current_game_data with sport-specific template"""
	global current_game_data, current_sport
	current_sport = sport.lower()
	if current_sport not in SPORT_CONFIGS:
		raise ValueError(f"Unsupported sport: {sport}. Supported sports: {list(SPORT_CONFIGS.keys())}")

	current_game_data = SPORT_CONFIGS[current_sport]['data_template'].copy()
	print(f"Initialized for {current_sport} with data template")

def main():
	# Sport Options: 'basketball', 'volleyball', 'football'
	SPORT = 'basketball'
	#SPORT = 'volleyball'

	# Initialize sport-specific data
	initialize_sport_data(SPORT)

	# Sport-specific URLs
	SPORT_URLS = {
		'basketball': "http://192.168.10.166//player/dataset/tables/RTD%2FAS5-Basketball.json",
		'volleyball': "http://192.168.10.166//player/dataset/tables/RTD%2FAS5-Volleyball.json",
		'football': ""
	}

	url = SPORT_URLS.get(SPORT)
	if not url:
		raise ValueError(f"No URL configured for sport: {SPORT}")

	print(f"Starting {SPORT} data server...")
	print(f"Data URL: {url}")
	print(f"Server will run on http://localhost:5000")
	print(f"Stats server listening on port 5001")

	# Create and start the data fetcher thread
	fetcher = SportDataFetcher(url, SPORT)
	fetch_thread = threading.Thread(target=update_data_loop, args=(fetcher,), daemon=True)
	fetch_thread.start()

	# Register hotkeys to pause/resume
	register_hotkeys()

	# Create and start the stats server thread
	stats_server = StatsServer()
	stats_thread = threading.Thread(target=stats_server.start, daemon=True)
	stats_thread.start()

	# Start heatmap server in separate thread
	heatmap_thread = threading.Thread(target=run_heatmap_server, daemon=True)
	heatmap_thread.start()

	# Run the Flask app
	app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
	main()
