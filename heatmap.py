import json
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import numpy as np

# Load JSON data
with open('Newton_PC_Boys.json') as f:
    data = json.load(f)

# Function to extract shot positions and made status for a given team
def extract_shots(team_players):
    shot_positions = []
    shot_made = []
    for player in team_players:
        for shot in player['Shots']:
            x, y = map(float, shot['ShotPosition'].split(','))
            if (x, y) != (0, 0):  # Skip shots at (0,0)
                shot_positions.append((x, y))
                shot_made.append(shot['Made'])
    return shot_positions, shot_made

# Extract shots for both teams
team1_shot_positions, team1_shot_made = extract_shots(data['Team1Players'])
team2_shot_positions, team2_shot_made = extract_shots(data['Team2Players'])

# Function to create heatmap for a given team
def create_heatmap(shot_positions, shot_made, team_name):
    # Load basketball court image and resize it to 1920x1050
    court_img = Image.open('court.png')
    court_img = court_img.resize((1920, 1050))
    court_width, court_height = court_img.size

    # Scale shot positions from 800x425 to 1920x1050
    scaled_shot_positions = [(x * (1920 / 800), y * (1050 / 425)) for x, y in shot_positions]

    # Separate made and missed shots
    made_shot_positions = [pos for pos, made in zip(scaled_shot_positions, shot_made) if made]
    missed_shot_positions = [pos for pos, made in zip(scaled_shot_positions, shot_made) if not made]

    # Create plot with white background
    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    ax.set_facecolor('white')
    fig.set_facecolor('white')

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
        cmap='inferno',  # Using inferno colormap like the NBA example
        fill=True, # Fills the area under the KDE curve.
        alpha=0.7, # Set transparency level
        levels=50,  # Increase number of contour levels for smoother gradient, 50 is a good value
        thresh=0, # Set threshold to 0 to include all data points
        ax=ax, # Plot on the same axis
        bw_adjust=0.8,  # Adjust bandwidth
        clip=((0, court_width), (0, court_height)),  # Clip KDE plot to court dimensions
        gridsize=100  # Increase grid size for smoother plot
    )

    # Add small dots for shot locations, green if made, red if missed
    for (x, y), made in zip(scaled_shot_positions, shot_made):
        if made:
            ax.scatter(x, y, c='green', marker='o', s=50, edgecolors='black', linewidths=1, alpha=0.6)
        else:
            ax.scatter(x, y, c='red', marker='x', s=50, linewidths=1, alpha=0.6)

    # Set plot limits to match the court image
    ax.set_xlim(0, court_width)
    ax.set_ylim(0, court_height)

    # Remove axes
    ax.set_axis_off()

    # Save plot to a file
    plt.savefig(f'heatmap_{team_name}.png', bbox_inches='tight', dpi=200)
    plt.close()

# Create heatmaps for both teams
create_heatmap(team1_shot_positions, team1_shot_made, 'Team1')
create_heatmap(team2_shot_positions, team2_shot_made, 'Team2')

# Create combined heatmap
combined_shot_positions = team1_shot_positions + team2_shot_positions
combined_shot_made = team1_shot_made + team2_shot_made
create_heatmap(combined_shot_positions, combined_shot_made, 'Combined')