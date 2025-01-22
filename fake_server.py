import threading
import random
import time
from datetime import datetime
from flask import Flask, jsonify, send_file, send_from_directory
import logging

app = Flask(__name__)

# Set the logging level to ERROR
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Global variables
shot_clock = 10
timeout_clock_min = 1
timeout_clock_sec = 30
shot_clock_status = "1"
current_game_data = {}
shot_clock = 15
timeout_clock_min = 1
timeout_clock_sec = 30

class BasketballDataFetcher:
	def __init__(self, url):
		self.url = url

	def fetch_data(self):
		# Generate fake data
		return generate_fake_data()

def generate_fake_data():
    global shot_clock
    global timeout_clock_min
    global timeout_clock_sec
    global shot_clock_status

    # Generate fake game clock data
    fake_data = {
        "clock": datetime.now().strftime("%M:%S.%f")[:-5],
        "shot_clock": str(shot_clock),
        "timeout_clock": f"{timeout_clock_min:02}:{timeout_clock_sec:02}",
        "shot_clock_status": str(shot_clock_status)
    }
    print(fake_data)

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
    global shot_clock_status
    while True:
        time.sleep(random.randint(3, 5))
        if shot_clock_status == "1":
            shot_clock_status = ""
        else:
            shot_clock_status = "1"

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

    # Start the shot clock toggling thread
    toggle_thread = threading.Thread(target=toggle_shot_clock)
    toggle_thread.daemon = True
    toggle_thread.start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()