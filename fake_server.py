import threading
import time
from datetime import datetime
from flask import Flask, jsonify, send_file, send_from_directory

app = Flask(__name__)
current_game_data = {}
shot_clock = 10  # Initialize shot clock to 10 seconds

class BasketballDataFetcher:
    def __init__(self, url):
        self.url = url

    def fetch_data(self):
        # Generate fake data
        return generate_fake_data()

def generate_fake_data():
    global shot_clock
    # Generate fake game clock data
    fake_data = {
        # Fake game clock in MM:SS.sss format
        #"clock": time.strftime("%M:%S", time.gmtime(time.time() % 600))
        #"clock": time.strftime("%M:%S") + f".{int(time.time() * 1000) % 1000:03d}",
        #"clock": time.strftime("%M:%S") + f".{int(time.time() * 100) % 10}",
        "clock": datetime.now().strftime("%M:%S.%f")[:-5],
        "shot_clock": str(shot_clock),
    }
    print(fake_data)

	# Decrement the shot clock
    shot_clock -= 1
    if shot_clock <= 0:
        shot_clock = 10  # Reset shot clock to 10 seconds

    return fake_data

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

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()