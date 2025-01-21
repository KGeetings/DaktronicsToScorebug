import time
import threading

# Initialize the counter
counter = 0
filename = "E:/VSCode/TestPython/Daktronic_Scorebug_Parser/game_data/Main_Clock_Time__mm_ss_ss_t__.txt"

def update_file():
    global counter
    while True:
        # Increment the counter
        counter += 1

        # Write the counter value to the file
        with open(filename, 'w') as f:
            f.write(str(counter))

        # Wait for 100 milliseconds
        time.sleep(0.1)

#Create file with initial value
with open(filename, 'w') as f:
	f.write(str(counter))

# Start the file update in a separate thread
thread = threading.Thread(target=update_file)
thread.start()

# Keep the main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated.")