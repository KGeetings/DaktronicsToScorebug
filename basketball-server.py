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

# Set the logging level to ERROR
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Create Flask app with static file support
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Enable CORS for all routes

# Global variables to store the game data
current_game_data = {
	'clock': '55:55',
	'home_score': '1',
	'guest_score': '1',
	'home_timeouts': 'III',
	'guest_timeouts': 'III',
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
}

class StatsServer:
	"""
	The stats message format should be JSON:
		{
			"command": "stats",
			"team": "home",  // or "guest"
			"text": "<html formatted stats>",
			"duration": 10  // seconds (0 for infinite)
		}
	To clear all stats:
		{
			"command": "clear_all"
		}
	Program will need to implement the following:
		Connects to the socket server (port 5001)
		Sends messages with a 4-byte length prefix (network byte order)
		Formats the JSON messages as shown above
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
				# First receive the message length (4 bytes)
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
			elif data.get('command') == 'stats':
				team = data.get('team', '').lower()
				if team in ['home', 'guest']:
					current_game_data[f'{team}_stats'] = data.get('text', '')
					current_game_data[f'{team}_stats_duration'] = data.get('duration', 0)

					# If duration is not 0 (infinite), start a timer to clear the stats
					if data.get('duration', 0) > 0:
						def clear_stats():
							time.sleep(data['duration'])
							current_game_data[f'{team}_stats'] = ''
							current_game_data[f'{team}_stats_duration'] = 0

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
			'Time_Out_Time__mm_ss____': 'timeout_clock',
			'Shot_Clock__0______or__z__': 'shot_clock_status',
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

	# Create and start the stats server thread
	stats_server = StatsServer()
	stats_thread = threading.Thread(target=stats_server.start, daemon=True)
	stats_thread.start()

	# Run the Flask app
	app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
	main()