import json
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import numpy as np
import cv2
from datetime import datetime
import io

# Set width and height
shot_width_x = 800 # Determined by StatsAppClient
shot_height_y = 671 # Determined by StatsAppClient
court_width_x = 1920 # Determined by Court.png
court_height_y = 1610 # Determined by Court.png

# Video configuration
VIDEO_FPS = 30 # Frames per second for the video
SHOT_DISPLAY_DURATION = 1.0 # How long each shot stays visible (in seconds)
SHOT_APPEARANCE_SPEED = (
0.5  # Multiplier for how fast shots appear (0.5 = half speed, 2.0 = double speed)
)

# Load JSON data
""" with open("X:\\data.json") as f:
	data = json.load(f) """

with open('W:\\PC vs Montezuma Girls.json') as f:
	data = json.load(f)

# Set font properties
plt.rcParams["font.family"] = "Rubik"
plt.rcParams["font.sans-serif"] = "Rubik"

"""
"Team1Players": [
	{
	  "PlayerName": "Jessa De Vries",
	  "PlayerNumber": "1",
	  "PlayerGrade": null,
	  "PlayerHeight": null,
	  "PlayerPosition": null,
	  "GUID": "4c466e79-f873-4e4f-ac50-5fa90b065e93",
	  "Team": 1,
	  "Shots": [
		{
		  "PointValue": 2,
		  "GUID": "783c465f-f68a-4c13-b572-63ab64627eff",
		  "PointCredit": 2,
		  "ShotPosition": "465.6716417910448,222.8805970149254",
		  "RealTime": "2025-12-08T18:21:28.5636579-06:00",
		  "FriendlyTime": "6:21 PM (0 min 0 sec ago)",
		  "FriendlyShotValue": "Two Points",
		  "GameTime": null,
		  "Made": true,
		  "ModifiedDate": "0001-01-01T00:00:00"
		}
	  ],
	  "PlayerFouls": 0,
	  "PlayerPoints": 2,
	  "PlayerThrees": 0,
	  "PlayerFrees": 0,
	  "AttemptedFrees": 0,
	  "AttemptedThrees": 0,
	  "Stats": "Ps: 2, Fs: 0, 3s:  0, 1s: 0",
	  "ShortenedName": "J. De Vries",
	  "FullStats": "Points: 0\nFouls: 0\nThrees: 0\nFrees: 0"
	},
"""

# Function to extract shot positions and made status for a given team
def extract_shots(team_players):
	global shot_width_x, shot_height_y
	shot_positions = []
	shot_made = []
	shot_time = []
	shot_details = []
	for player in team_players:
		for shot in player["Shots"]:
			x, y = map(float, shot["ShotPosition"].split(","))
			if (x, y) != (0, 0):  # Filter out free throws
				if (0 <= x <= shot_width_x and 0 <= y <= shot_height_y):  # Filter out invalid shots, and free throws
					# Flip the Y coordinate
					y = shot_height_y - y
					shot_positions.append((x, y))
					shot_made.append(shot["Made"])
					shot_time.append(shot["RealTime"])
					shot_details.append(
						{
							"player": player["PlayerName"],
							"made": shot["Made"],
							"point_value": shot["PointValue"],
							"time": shot["RealTime"],
						}
					)
				else:
					print(
						f"Invalid shot detected for player {player['PlayerName']} at position ({x}, {y})"
					)
	return shot_positions, shot_made, shot_time, shot_details

def extract_team_names(data):
	team1 = data["Team1Name"]
	team2 = data["Team2Name"]
	return team1, team2

# Function to calculate shot percentages
def calculate_percentages(team_players):
	total_shots = 0
	made_threes = 0
	made_twos = 0
	made_frees = 0
	attempted_threes = 0
	attempted_twos = 0
	attempted_frees = 0

	for player in team_players:
		for shot in player["Shots"]:
			total_shots += 1
			if shot["PointValue"] == 3:
				attempted_threes += 1
				if shot["Made"]:
					made_threes += 1
			elif shot["PointValue"] == 2:
				attempted_twos += 1
				if shot["Made"]:
					made_twos += 1
			elif shot["PointValue"] == 1:
				attempted_frees += 1
				if shot["Made"]:
					made_frees += 1

	three_percentage = (made_threes / attempted_threes * 100) if attempted_threes else 0
	two_percentage = (made_twos / attempted_twos * 100) if attempted_twos else 0
	free_percentage = (made_frees / attempted_frees * 100) if attempted_frees else 0

	return (
		three_percentage,
		two_percentage,
		free_percentage,
		made_threes,
		attempted_threes,
		made_twos,
		attempted_twos,
		made_frees,
		attempted_frees,
	)

# Function to convert matplotlib figure to numpy array for video
def fig_to_array(fig):
	"""Convert matplotlib figure to numpy array"""
	fig.canvas.draw()
	image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
	image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
	return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

# Function to create video with shots appearing in chronological order
def create_shot_timeline_video(
		shot_positions,
		shot_made,
		shot_times,
		shot_details,
		team_name,
		video_filename,
		appearance_speed=1.0,
	):
	if not shot_positions or not shot_times:
		print(f"No shot data available for {team_name}. Skipping video creation.")
		return

	# Sort shots by time
	sorted_indices = sorted(range(len(shot_times)), key=lambda i: shot_times[i])
	sorted_positions = [shot_positions[i] for i in sorted_indices]
	sorted_made = [shot_made[i] for i in sorted_indices]
	sorted_details = [shot_details[i] for i in sorted_indices]

	# Load court image
	court_img = Image.open("court-one-side-eagle.png")
	court_img = court_img.resize((court_width_x, court_height_y))
	court_array = np.array(court_img)
	court_array_bgr = cv2.cvtColor(court_array, cv2.COLOR_RGB2BGR)

	# Scale shot positions
	scaled_shot_positions = [
		(x * (court_width_x / shot_width_x), y * (court_height_y / shot_height_y))
		for x, y in shot_positions
	]

	# Create video writer
	fourcc = cv2.VideoWriter_fourcc(*"mp4v")
	out = cv2.VideoWriter(
		video_filename, fourcc, VIDEO_FPS, (court_width_x, court_height_y)
	)

	# Calculate frames per shot
	frames_per_shot = int(SHOT_DISPLAY_DURATION * VIDEO_FPS * appearance_speed)
	frames_per_shot = max(1, frames_per_shot)  # At least 1 frame

	current_shots = []  # Accumulate shots on court

	# Generate frames
	total_frames = len(shot_positions) * frames_per_shot
	print(f"Creating video: {video_filename}")
	print(f"Total frames: {total_frames}, FPS: {VIDEO_FPS}")

	for frame_num in range(total_frames):
		global end_frame
		frame = court_array_bgr.copy()

		# Determine which shot should appear at this frame
		shot_idx = min(frame_num // frames_per_shot, len(sorted_positions) - 1)

		# Add the new shot to current shots if we just reached it
		if shot_idx < len(sorted_positions):
			current_shots = sorted_positions[: shot_idx + 1]
			current_made = sorted_made[: shot_idx + 1]

		# Draw all current shots
		for (x, y), made in zip(current_shots, current_made):
			if made:
				cv2.circle(
					frame, (int(x), int(y)), 15, (0, 255, 0), -1
				)  # Green filled circle
				cv2.circle(frame, (int(x), int(y)), 15, (0, 0, 0), 2)  # Black border
			else:
				cv2.line(
					frame,
					(int(x) - 10, int(y) - 10),
					(int(x) + 10, int(y) + 10),
					(0, 0, 255),
					3,
				)  # Red X
				cv2.line(
					frame,
					(int(x) - 10, int(y) + 10),
					(int(x) + 10, int(y) - 10),
					(0, 0, 255),
					3,
				)

		# Add shot counter
		counter_text = f"Shot {shot_idx + 1}/{len(sorted_positions)}"
		cv2.putText(
			frame,
			counter_text,
			(30, court_height_y - 30),
			cv2.FONT_HERSHEY_SIMPLEX,
			1.0,
			(255, 255, 255),
			2,
		)
		end_frame = frame
		out.write(frame)

	shot_frame_end_buffer = 30
	for i in range(shot_frame_end_buffer):
		out.write(end_frame)
	out.release()
	print(f"Video saved: {video_filename}")


# Extract team names
team1_name, team2_name = extract_team_names(data)

# Extract shots for both teams (now includes shot_details)
team1_shot_positions, team1_shot_made, team1_shot_time, team1_shot_details = (
	extract_shots(data["Team1Players"])
)
team2_shot_positions, team2_shot_made, team2_shot_time, team2_shot_details = (
	extract_shots(data["Team2Players"])
)

# Calculate percentages for both teams
team1_percentages = calculate_percentages(data["Team1Players"])
team2_percentages = calculate_percentages(data["Team2Players"])


# Function to create heatmap for a given team
def create_heatmap(
	shot_positions, shot_made, team_name, team_num, percentages, player_names=None
):
	if not shot_positions or not shot_made:
		print(f"No shot data available for {team_name}. Skipping heatmap creation.")
		return

	# Load basketball court image and resize it to court_width_x, court_height_y
	court_img = Image.open("court-one-side-eagle.png")
	court_img = court_img.resize((court_width_x, court_height_y))
	court_width, court_height = court_img.size

	# Scale shot positions from shot_width_x, shot_height_y to court_width_x, court_height_y
	scaled_shot_positions = [
		(x * (court_width_x / shot_width_x), y * (court_height_y / shot_height_y))
		for x, y in shot_positions
	]

	# Separate made and missed shots
	made_shot_positions = [
		pos for pos, made in zip(scaled_shot_positions, shot_made) if made
	]
	missed_shot_positions = [
		pos for pos, made in zip(scaled_shot_positions, shot_made) if not made
	]

	# Create plot with white background
	fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
	ax.set_facecolor("white")
	fig.set_facecolor("white")

	# Display court image
	ax.imshow(court_img, extent=[0, court_width, 0, court_height])

	# Convert made shot positions to arrays for plotting
	if made_shot_positions:
		x_coords, y_coords = zip(*made_shot_positions)
	else:
		x_coords, y_coords = [], []

	# Create heatmap using KDE plot
	sns.kdeplot(
		x=x_coords,
		y=y_coords,
		cmap="inferno",  # Using inferno colormap
		fill=True,  # Fills the area under the KDE curve
		alpha=0.7,  # Set transparency level
		levels=50,  # Increase number of contour levels for smoother gradient, 50 is a good value
		thresh=0,  # Set threshold to 0 to include all data points
		ax=ax,  # Plot on the same axis
		bw_adjust=0.9,  # Adjust bandwidth
		clip=(
			(0, court_width_x),
			(0, court_height_y),
		),  # Clip KDE plot to court dimensions
		gridsize=100,  # Increase grid size for smoother plot
		cut=100,
	)

	# Add small dots for shot locations, green if made, red if missed
	for (x, y), made in zip(scaled_shot_positions, shot_made):
		if made:
			ax.scatter(
				x,
				y,
				c="green",
				marker="o",
				s=200,
				edgecolors="black",
				linewidths=2,
				alpha=0.6,
			)
		else:
			ax.scatter(x, y, c="red", marker="x", s=200, linewidths=3, alpha=0.6)

	# Set plot limits to match the court image
	ax.set_xlim(0, court_width_x)
	ax.set_ylim(0, court_height_y)

	# Remove axes
	ax.set_axis_off()

	# Add title to the heatmap
	ax.set_title(f"{team_name} Shot Heatmap", fontsize=16, color="black")

	# Add text for percentages below the graph
	(
		three_percentage,
		two_percentage,
		free_percentage,
		made_threes,
		attempted_threes,
		made_twos,
		attempted_twos,
		made_frees,
		attempted_frees,
	) = percentages
	fig.text(
		0.5,
		0.04,
		f"Three-Points: {made_threes}/{attempted_threes} ({three_percentage:.2f}%) | Two-Points: {made_twos}/{attempted_twos} ({two_percentage:.2f}%)\nFree Throw: {made_frees}/{attempted_frees} ({free_percentage:.2f}%)",
		color="black",
		fontsize=18,
		ha="center",
	)

	# Add player names below the percentages if provided
	if player_names:
		fig.text(
			0.5,
			0.93,
			f'Players: {", ".join(player_names)}',
			color="black",
			fontsize=12,
			ha="center",
		)

	# Save plot to a file
	plt.savefig(f"heatmap_{team_num}.png", bbox_inches="tight", dpi=200)
	# plt.show()
	plt.close()


# Function to create heatmap for individual players
def create_individual_heatmap(team_num, player_numbers):
	if team_num == 1:
		team_players = data["Team1Players"]
		team_name = team1_name
	else:
		team_players = data["Team2Players"]
		team_name = team2_name

	selected_players = [
		player for player in team_players if player["PlayerNumber"] in player_numbers
	]
	shot_positions, shot_made, shot_time, shot_details = extract_shots(selected_players)
	if not shot_positions or not shot_made:
		print(
			f"No shot data available for selected players in {team_name}. Skipping heatmap creation."
		)
		return

	percentages = calculate_percentages(selected_players)
	player_names = [player["PlayerName"] for player in selected_players]

	create_heatmap(
		shot_positions,
		shot_made,
		f"{team_name} Selected Players",
		f"Team{team_num}_Selected",
		percentages,
		player_names,
	)

# Create heatmaps for both teams
create_heatmap(
	team1_shot_positions, team1_shot_made, f"{team1_name}", "team1", team1_percentages
)
create_heatmap(
	team2_shot_positions, team2_shot_made, f"{team2_name}", "team2", team2_percentages
)

# Create combined heatmap
combined_shot_positions = team1_shot_positions + team2_shot_positions
combined_shot_made = team1_shot_made + team2_shot_made
combined_percentages = calculate_percentages(
	data["Team1Players"] + data["Team2Players"]
)
create_heatmap(
	combined_shot_positions,
	combined_shot_made,
	f"{team1_name} and {team2_name} Combined",
	"Combined",
	combined_percentages,
)

# Create shot timeline videos
# Adjust SHOT_APPEARANCE_SPEED to control how fast shots appear:
# 0.5 = half speed (slower), 1.0 = normal, 2.0 = double speed (faster)
create_shot_timeline_video(
	team1_shot_positions,
	team1_shot_made,
	team1_shot_time,
	team1_shot_details,
	team1_name,
	f'shot_timeline_{team1_name.replace(" ", "_")}.mp4',
	SHOT_APPEARANCE_SPEED,
)
""" create_shot_timeline_video(
	team2_shot_positions,
	team2_shot_made,
	team2_shot_time,
	team2_shot_details,
	team2_name,
	f'shot_timeline_{team2_name.replace(" ", "_")}.mp4',
	SHOT_APPEARANCE_SPEED,
)
create_shot_timeline_video(
	combined_shot_positions,
	combined_shot_made,
	team1_shot_time + team2_shot_time,
	team1_shot_details + team2_shot_details,
	f"{team1_name} and {team2_name}",
	f"shot_timeline_combined.mp4",
	SHOT_APPEARANCE_SPEED,
) """

# Example usage for individual players
create_individual_heatmap(1, ["1"])  # Team 1 (Eagles), players 2 and 4
create_individual_heatmap(2, ["10"])  # Team 2, players 1 and 3
