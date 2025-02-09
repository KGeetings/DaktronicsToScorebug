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

def extract_team_names(data):
    team1 = data['Team1Name']
    team2 = data['Team2Name']
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
        for shot in player['Shots']:
            total_shots += 1
            if shot['PointValue'] == 3:
                attempted_threes += 1
                if shot['Made']:
                    made_threes += 1
            elif shot['PointValue'] == 2:
                attempted_twos += 1
                if shot['Made']:
                    made_twos += 1
            elif shot['PointValue'] == 1:
                attempted_frees += 1
                if shot['Made']:
                    made_frees += 1

    three_percentage = (made_threes / attempted_threes * 100) if attempted_threes else 0
    two_percentage = (made_twos / attempted_twos * 100) if attempted_twos else 0
    free_percentage = (made_frees / attempted_frees * 100) if attempted_frees else 0

    return three_percentage, two_percentage, free_percentage

# Extract team names
team1_name, team2_name = extract_team_names(data)

# Extract shots for both teams
team1_shot_positions, team1_shot_made = extract_shots(data['Team1Players'])
team2_shot_positions, team2_shot_made = extract_shots(data['Team2Players'])

# Calculate percentages for both teams
team1_percentages = calculate_percentages(data['Team1Players'])
team2_percentages = calculate_percentages(data['Team2Players'])

# Function to create heatmap for a given team
def create_heatmap(shot_positions, shot_made, team_name, team_num, percentages, player_names=None):
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

    # Add title to the heatmap
    ax.set_title(f'{team_name} Shot Heatmap', fontsize=16, color='black')

    # Add text for percentages below the title
    three_percentage, two_percentage, free_percentage = percentages
    fig.text(0.5, 0.92, f'Three-Point %: {three_percentage:.2f}% | Two-Point %: {two_percentage:.2f}% | Free Throw %: {free_percentage:.2f}%', color='black', fontsize=12, ha='center')

    # Add player names below the percentages if provided
    if player_names:
        fig.text(0.5, 0.88, f'Players: {", ".join(player_names)}', color='black', fontsize=12, ha='center')

    # Save plot to a file
    plt.savefig(f'heatmap_{team_num}.png', bbox_inches='tight', dpi=200)
    plt.close()

# Function to create heatmap for individual players
def create_individual_heatmap(team_num, player_numbers):
    if team_num == 1:
        team_players = data['Team1Players']
        team_name = team1_name
    else:
        team_players = data['Team2Players']
        team_name = team2_name

    selected_players = [player for player in team_players if player['PlayerNumber'] in player_numbers]
    shot_positions, shot_made = extract_shots(selected_players)
    percentages = calculate_percentages(selected_players)
    player_names = [player['PlayerName'] for player in selected_players]

    create_heatmap(shot_positions, shot_made, f'{team_name} Selected Players', f'Team{team_num}_Selected', percentages, player_names)

# Create heatmaps for both teams
create_heatmap(team1_shot_positions, team1_shot_made, f'{team1_name}', "team1", team1_percentages)
create_heatmap(team2_shot_positions, team2_shot_made, f'{team2_name}', "team2", team2_percentages)

# Create combined heatmap
combined_shot_positions = team1_shot_positions + team2_shot_positions
combined_shot_made = team1_shot_made + team2_shot_made
combined_percentages = calculate_percentages(data['Team1Players'] + data['Team2Players'])
create_heatmap(combined_shot_positions, combined_shot_made, f'{team1_name} and {team2_name} Combined', "Combined", combined_percentages)

# Example usage for individual players
create_individual_heatmap(1, ["2", "4"]) # Team 1, players 2 and 4
create_individual_heatmap(2, ["1", "3"]) # Team 2, players 1 and 3