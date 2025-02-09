import json
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import numpy as np

# Load JSON data
with open('Newton_PC_Boys.json') as f:
    data = json.load(f)

# Extract shot positions
shot_positions = []
shot_made = []

for player in data['Team1Players'] + data['Team2Players']:
    for shot in player['Shots']:
        x, y = map(float, shot['ShotPosition'].split(','))
        shot_positions.append((x, y))
        shot_made.append(shot['Made'])

# Load basketball court image and resize it to 800x425
court_img = Image.open('court.png')
court_img = court_img.resize((800, 425))
court_width, court_height = court_img.size

# Create plot
fig, ax = plt.subplots(figsize=(12, 8))
ax.imshow(court_img, extent=[0, court_width, 0, court_height])

# Separate made and missed shots
made_shots = [pos for pos, made in zip(shot_positions, shot_made) if made]
missed_shots = [pos for pos, made in zip(shot_positions, shot_made) if not made]

# Plot made shots with both heatmap and scatter
if made_shots:
    made_x, made_y = zip(*made_shots)
    # Reduced bandwidth for sparse data
    sns.kdeplot(x=made_x, y=made_y, ax=ax, cmap='Greens', fill=True,
                alpha=0.4, thresh=0, bw_adjust=1.5, warn_singular=False)
    # Add scatter plot on top
    ax.scatter(made_x, made_y, c='green', alpha=0.6, s=100)

# Plot missed shots with both heatmap and scatter
if missed_shots:
    missed_x, missed_y = zip(*missed_shots)
    # Reduced bandwidth for sparse data
    sns.kdeplot(x=missed_x, y=missed_y, ax=ax, cmap='Reds', fill=True,
                alpha=0.4, thresh=0, bw_adjust=1.5, warn_singular=False)
    # Add scatter plot on top
    ax.scatter(missed_x, missed_y, c='red', alpha=0.6, s=100)

# Set plot limits to match the court image
ax.set_xlim(0, court_width)
ax.set_ylim(0, court_height)

# Add legend
ax.legend()

# Remove axes
ax.set_axis_off()

# Show plot
plt.show()