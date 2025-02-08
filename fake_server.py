import threading
import random
import time
from datetime import datetime
from flask import Flask, jsonify, send_file, send_from_directory
import logging
import keyboard

app = Flask(__name__)

# Set the logging level to ERROR
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Global variables
shot_clock_status = "1"
current_game_data = {}
shot_clock = 15
timeout_clock_min = 0
timeout_clock_sec = 20
guest_stats = "Test Guest Data"
home_stats = "Test Home Data"
home_stats_duration = 3
guest_stats_duration = 3
home_score = 0
guest_score = 0
home_timeouts = 5
guest_timeouts = 5
home_fouls = 0
guest_fouls = 0

class BasketballDataFetcher:
	def __init__(self, url):
		self.url = url

	def fetch_data(self):
		# Generate fake data
		return generate_fake_data()

def update_stats():
	global home_score, guest_score, home_fouls, guest_fouls, home_timeouts, guest_timeouts, guest_stats, home_stats, home_stats_duration, guest_stats_duration

	home_score += 3
	guest_score += 1
	home_fouls += 1
	guest_fouls += 1
	home_timeouts -= 1
	guest_timeouts -= 1

	# Generate new stats data
	guest_stats = f'<div style="color:black;"><b>And One</b></div>#2 - Jacob Harman<br>Fouls: {home_fouls}&emsp;&emsp;Points: {home_score}<hr style="border-color:white;width:1500px;"<br>Shot 1 - Made<br>Shot 2 - Made'
	#home_stats = f'<div style="color:black;"><b>Three Points</b></div>#1 - Kenyon Geetings<br>Fouls: {home_fouls}&emsp;&emsp;Points: {home_score}'
	home_stats = f'<div style="color:black;"><b>Fouled By</b></div>#1 - Kenyon Geetings<br>Fouls: {home_fouls}&emsp;&emsp;Points: {home_score}'

	# Reset scores and timeouts if needed
	if home_score > 15:
		home_score = 0
	if home_timeouts < 0:
		home_timeouts = 5
		guest_timeouts = 5

def generate_fake_data():
	global shot_clock
	global timeout_clock_min
	global timeout_clock_sec
	global shot_clock_status
	global guest_stats
	global home_stats
	global home_score
	global guest_score
	global home_timeouts
	global guest_timeouts
	global home_fouls
	global guest_fouls
	global home_stats_duration
	global guest_stats_duration

	# Generate fake game clock data
	fake_data = {
		"clock": datetime.now().strftime("%M:%S.%f")[:-5],
		"shot_clock": str(shot_clock),
		"timeout_clock": f"{timeout_clock_min:02}:{timeout_clock_sec:02}",
		"home_stats": home_stats,
		"guest_stats": str(guest_stats),
		"home_score": str(home_score),
		"guest_score": str(guest_score),
		"home_timeouts": str(home_timeouts),
		"guest_timeouts": str(guest_timeouts),
		"home_fouls": str(home_fouls),
		"guest_fouls": str(guest_fouls),
		"period_desc": "5TH Quarter",
		'home_stats_duration': home_stats_duration,
		'guest_stats_duration': guest_stats_duration,
	}

	print("Home Stats: ", home_stats, "\tHome Stats Duration: ", home_stats_duration)

	# Decrement the shot clock only if the shot clock status is "1"
	if shot_clock_status == "1":
		shot_clock -= 1
		if shot_clock <= 0:
			shot_clock = 15  # Reset shot clock to 15 seconds

	# Decrement the timeout clock
	if timeout_clock_sec == 0:
		if timeout_clock_min > 0:
			timeout_clock_min -= 1
			timeout_clock_sec = 59
		else:
			timeout_clock_min = 1
			timeout_clock_sec = 30
	else:
		timeout_clock_sec -= 1

	return fake_data

def toggle_shot_clock():
	global shot_clock_status, home_stats_duration, guest_stats_duration
	if shot_clock_status == "1":
		shot_clock_status = ""
		home_stats_duration = 0
		guest_stats_duration = 0
	else:
		shot_clock_status = "1"
		home_stats_duration = 3
		guest_stats_duration = 3

def clear_stats():
	global guest_stats, home_stats, home_stats_duration, guest_stats_duration
	guest_stats = ""
	home_stats = ""
	home_stats_duration = 0
	guest_stats_duration = 0

def handle_keyboard_input():
	keyboard.on_press_key("n", lambda _: update_stats())
	keyboard.on_press_key("t", lambda _: toggle_shot_clock())
	keyboard.on_press_key("m", lambda _: clear_stats())

def update_data_loop(fetcher):
	global current_game_data
	while True:
		current_game_data = fetcher.fetch_data()
		time.sleep(1)

@app.route('/data')
def get_data():
	return jsonify(current_game_data)

@app.route('/')
def serve_html():
	return send_file('basketball-frontend.html')

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

	# Start keyboard listener
	keyboard_thread = threading.Thread(target=handle_keyboard_input, daemon=True)
	keyboard_thread.start()

	# Run the Flask app
	app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
	main()