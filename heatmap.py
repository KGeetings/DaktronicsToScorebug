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
        if (x, y) != (0, 0):  # Skip shots at (0,0)
            shot_positions.append((x, y))
            shot_made.append(shot['Made'])

print("Shot Positions: ", shot_positions)
# Load basketball court image and resize it to 800x425
court_img = Image.open('court.png')
court_img = court_img.resize((800, 425))
court_width, court_height = court_img.size

# Create plot with white background
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_facecolor('white')
fig.set_facecolor('white')

# Display court image
ax.imshow(court_img, extent=[0, court_width, 0, court_height])

# Convert shot positions to arrays for plotting
x_coords, y_coords = zip(*shot_positions)

# Create heatmap using KDE plot
sns.kdeplot(
    x=x_coords,
    y=y_coords,
    cmap='inferno',  # Using inferno colormap like the NBA example
    fill=True,
    alpha=0.6,
    levels=50,  # Increase number of contour levels for smoother gradient, 50 is a good value
    thresh=0,
    ax=ax
)

# Add small white dots for shot locations
#ax.scatter(x_coords, y_coords, c='white', s=2, alpha=0.3)

# Add small dots for shot locations, green if made, red if missed
colors = ['green' if made else 'red' for made in shot_made]
ax.scatter(x_coords, y_coords, c=colors, s=2, alpha=0.3)

# Set plot limits to match the court image
ax.set_xlim(0, court_width)
ax.set_ylim(0, court_height)

# Remove axes
ax.set_axis_off()

# Save plot to a file
plt.savefig('heatmap.png', bbox_inches='tight')